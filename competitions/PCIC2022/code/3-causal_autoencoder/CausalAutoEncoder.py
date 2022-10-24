# import tensorflow as tf
import tensorflow.compat.v1 as tf
tf.disable_v2_behavior()
import numpy as np
import scipy.optimize as sopt
import scipy.linalg as slin
import scipy.optimize as sopt
from sklearn import metrics
from sklearn import svm
# from utils import *

def Y_New(Y_in):
    cluster = np.unique(Y_in)
    Y = np.zeros((Y_in.shape[0], cluster.__len__()), dtype=int)
    for i in range(Y_in.shape[0]):
        for j in range(cluster.__len__()):
            if Y_in[i] == cluster[j]:
                Y[i][j] = 1
    return Y, cluster


def MBFeatures(array):
    n,p = array.shape
    array[np.abs(array) >= 0.3] = 1
    array[np.abs(array) < 0.3] = 0

    p = p -1
    parents = np.copy(array[0:p, p:p + 1])
    children = np.copy(array[ p:p + 1,0:p])
    MB = parents + np.transpose(children)

    for j in range(p):
        if children[0,j] == 1:
            MB = MB + array[0:p, j:j + 1]
    MB[np.abs(MB) >= 1] = 1
    return MB
    
    
def causal_structure_learning(X, lambda1=0.001, loss_type='l2', max_iter=100, h_tol=1e-8, rho_max=1e+16, w_threshold=0.3):
    """Solve min_W L(W; X)  s.t. h(W) = 0 using augmented Lagrangian.

    Args:
        X (np.ndarray): [n, d] sample matrix
        lambda1 (float): l1 penalty parameter
        loss_type (str): l2, logistic, poisson
        max_iter (int): max num of dual ascent steps
        h_tol (float): exit if |h(w_est)| <= htol
        rho_max (float): exit if rho >= rho_max
        w_threshold (float): drop edge if |weight| < threshold

    Returns:
        W_est (np.ndarray): [d, d] estimated DAG
    """

    def _loss(W):
        """Evaluate value and gradient of loss."""
        M = X @ W
        if loss_type == 'l2':
            R = X - M
            loss = 0.5 / X.shape[0] * (R ** 2).sum()
            G_loss = - 1.0 / X.shape[0] * X.T @ R
        elif loss_type == 'logistic':
            loss = 1.0 / X.shape[0] * (np.logaddexp(0, M) - X * M).sum()
            G_loss = 1.0 / X.shape[0] * X.T @ (sigmoid(M) - X)
        elif loss_type == 'poisson':
            S = np.exp(M)
            loss = 1.0 / X.shape[0] * (S - X * M).sum()
            G_loss = 1.0 / X.shape[0] * X.T @ (S - X)
        else:
            raise ValueError('unknown loss type')
        return loss, G_loss

    def _h(W):
        """Evaluate value and gradient of acyclicity constraint."""
        #     E = slin.expm(W * W)
        #     h = np.trace(E) - d
        M = np.eye(d) + W * W / d
        E = np.linalg.matrix_power(M, d - 1)
        h = (E.T * M).sum() - d
        G_h = E.T * W * 2
        return h, G_h

    def _adj(w):
        """Convert doubled variables ([2 d^2] array) back to original variables ([d, d] matrix)."""
        return (w[:d * d] - w[d * d:]).reshape([d, d])

    def _func(w):
        """Evaluate value and gradient of augmented Lagrangian for doubled variables ([2 d^2] array)."""
        W = _adj(w)
        loss, G_loss = _loss(W)
        h, G_h = _h(W)
        obj = loss + 0.5 * rho * h * h + alpha * h + lambda1 * w.sum()
        G_smooth = G_loss + (rho * h + alpha) * G_h
        g_obj = np.concatenate((G_smooth + lambda1, - G_smooth + lambda1), axis=None)
        return obj, g_obj

    n, d = X.shape
    w_est, rho, alpha, h = np.zeros(2 * d * d), 1.0, 0.0, np.inf  # double w_est into (w_pos, w_neg)
    bnds = [(0, 0) if i == j else (0, None) for _ in range(2) for i in range(d) for j in range(d)]
    for iter_j in range(max_iter):
        w_new, h_new = None, None
        print(iter_j)
        while rho < rho_max:
            sol = sopt.minimize(_func, w_est, method='L-BFGS-B', jac=True, bounds=bnds)
            w_new = sol.x
            h_new, _ = _h(_adj(w_new))
            if h_new > 0.25 * h:
                rho *= 10
            else:
                break
        w_est, h = w_new, h_new
        alpha += rho * h
        if h <= h_tol or rho >= rho_max:
            break
    W_est = _adj(w_est)
    # print(W_est)
    W_est[np.abs(W_est) < w_threshold] = 0
    # print(W_est)
    return W_est, h


def causal_autoencoder_two_layer(X_in, Y_in, learning_rate, num_steps, tol, num_hidden_1, num_hidden_2):
    n, p = X_in.shape
    display_step = 1000


    Weight_A_in = np.eye(num_hidden_2 + 1, num_hidden_2 + 1, dtype=float)
    Weight_P_in = np.ones((n,num_hidden_2))

    X = tf.placeholder("float", [None, p])
    Y = tf.placeholder("float", [None, 1])

    Weight_A = tf.placeholder("float", [num_hidden_2+1, num_hidden_2+1])
    Weight_P = tf.placeholder("float", [n,  num_hidden_2])

    betas = {
        'encoder_h1': tf.Variable(tf.random_normal([p, num_hidden_1])),
        'encoder_h2': tf.Variable(tf.random_normal([num_hidden_1, num_hidden_2])),
        'decoder_h1': tf.Variable(tf.random_normal([num_hidden_2, num_hidden_1])),
        'decoder_h2': tf.Variable(tf.random_normal([num_hidden_1, p])),
    }
    biases = {
        'encoder_b1': tf.Variable(tf.random_normal([num_hidden_1])),
        'encoder_b2': tf.Variable(tf.random_normal([num_hidden_2])),
        'decoder_b1': tf.Variable(tf.random_normal([num_hidden_1])),
        'decoder_b2': tf.Variable(tf.random_normal([p])),
    }

    def encoder(x):
        # Encoder Hidden layer with sigmoid activation
        layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, betas['encoder_h1']), biases['encoder_b1']))
        layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, betas['encoder_h2']), biases['encoder_b2']))
        return layer_2

    # Building the decoder
    def decoder(x):
        # Decoder Hidden layer with sigmoid activation
        layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, betas['decoder_h1']), biases['decoder_b1']))
        layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, betas['decoder_h2']), biases['decoder_b2']))
        return layer_2

    # Construct model
    X_encoder = encoder(X)
    x_reconstraction = decoder(X_encoder)
    x_true = X
    X_encoder_lable = tf.concat([X_encoder, Y], 1)

    
    # prediction
    W = tf.Variable(tf.random_normal([num_hidden_2, 1]))
    b = tf.Variable(tf.random_normal([1]))
    hypothesis = tf.nn.sigmoid(tf.matmul(tf.multiply(X_encoder,Weight_P), W) + b)

    saver = tf.train.Saver()
    sess = tf.Session()

    L_D = tf.reduce_mean(tf.pow(x_reconstraction - x_true, 2)) / 2

    L_Y = -tf.reduce_mean(Y * tf.log(tf.clip_by_value(hypothesis, 1e-8, 1.0)) + (1 - Y) * tf.log(tf.clip_by_value(1 - hypothesis, 1e-8, 1.0)))

    L_R = tf.reduce_sum(tf.square(betas['encoder_h1'])) + tf.reduce_sum(tf.square(betas['encoder_h2'])) + tf.reduce_sum(tf.square(betas['decoder_h1'])) + tf.reduce_sum(
        tf.square(betas['decoder_h2'])) + tf.reduce_sum(biases['encoder_b1']**2) + tf.reduce_sum(biases['decoder_b1']**2) + tf.reduce_sum(biases['encoder_b2']**2) + tf.reduce_sum(biases['decoder_b2']**2) + tf.reduce_sum(W**2) + tf.reduce_sum(b**2)

    L_C = tf.reduce_mean(tf.pow(X_encoder_lable - tf.matmul(X_encoder_lable, Weight_A), 2))

    # loss = 1.0 * L_D + 0.001 * L_R + 1 * L_C + 0.1 * L_Y
    # loss = 1.0 * L_D + 0.0001 * L_R + 10 * L_C + 0.1 * L_Y
    loss = 1.0 * L_D + 0.0001 * L_R + 10 * L_C + 0.1 * L_Y
    optimizer = tf.train.RMSPropOptimizer(learning_rate).minimize(loss)

    max_iter = 10
    sess.run(tf.global_variables_initializer())
    for iter_k in range(1, max_iter+1):
        l_pre = 0
        for i in range(1, num_steps + 1):
            _, l, l_autoencoder, l_netPara_l21, l_causal_recon, loss_pre = sess.run(
                [optimizer, loss, L_D, L_R, L_C, L_Y],
                feed_dict={X: X_in, Y: Y_in, Weight_A: Weight_A_in,Weight_P: Weight_P_in})
            if abs(l - l_pre) <= tol:
                print('Converge ... Step %i: Minibatch Loss: %f ... %f ... %f ... %f ... %f' % ( i, l, l_autoencoder, l_netPara_l21, l_causal_recon,loss_pre))
                break
            l_pre = l
            if i % display_step == 0 or i == 1:
                print('Converge ... Step %i: Minibatch Loss: %f  ... %f  ... %f ... %f ... %f' % (i, l, l_autoencoder, l_netPara_l21, l_causal_recon,loss_pre))

        Encoder, w1, b1, w2, b2 = sess.run([X_encoder, betas['encoder_h1'],  biases['encoder_b1'], betas['encoder_h2'],  biases['encoder_b2']], feed_dict={X: X_in, Y: Y_in, Weight_A: Weight_A_in})
  
        if iter_k < max_iter:
            W_est, global_loss= causal_structure_learning(np.hstack((Encoder, Y_in)), lambda1=0, loss_type='l2')
            Weight_A_in = np.copy(W_est)
            Temp = np.copy(W_est)
            Temp[np.abs(Temp) >= 0.3] = 1
            B = MBFeatures(Temp)
            Weight_P_in = np.copy(np.tile(np.transpose(B), (n,1)))

    Encoder, w1, b1, w2, b2 = sess.run(
        [X_encoder, betas['encoder_h1'], biases['encoder_b1'], betas['encoder_h2'], biases['encoder_b2']],
        feed_dict={X: X_in, Y: Y_in, Weight_A: Weight_A_in})
    return Encoder, w1, b1, w2, b2, W_est











