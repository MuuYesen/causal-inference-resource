def fun(topology_data):
    clusters = []
    ii = list(range(topology_data.shape[0]))
    nu = 0
    for i in range(topology_data.shape[0]):
        if i not in ii:
            continue
        cluster = [i]
        ii.remove(i)
        run = True
        while run:
            run = False
            for j in ii:
                if topology_data[j, cluster].sum() > 0:
                    cluster.append(j)
                    ii.remove(j)
                    run = True
                    nu += 1
                    # print(nu)
        clusters.append(cluster)
    return clusters