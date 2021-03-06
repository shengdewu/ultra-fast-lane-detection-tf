import tensorflow as tf

def similaryit_loss(label):
    batch, rows, lanes, cells = label.get_shape()
    loss_all = list()
    for i in range(rows-1):
        loss_all.append(tf.abs(label[:,i,:,:] - label[:,i+1,:,:]))

    loss = tf.concat(loss_all, 0)
    less_one = tf.cast(tf.less(loss, 1.0), tf.float32)
    smooth_l1_loss = (less_one * 0.5 * loss **2) + (1.0-less_one) * (loss-0.5)
    return tf.reduce_mean(smooth_l1_loss)

def structural_loss(label):
    batch, rows, lanes, cells = label.get_shape()
    prob = tf.nn.softmax(label[:,:,:,0:cells-1], -1)
    k = tf.convert_to_tensor([i for i in range(1, cells)], dtype=tf.float32)
    loc = tf.reduce_sum(prob * k, -1)
    loss_all = list()
    for i in range(0, rows//2):
        loss_all.append(tf.abs((loc[:,i,:]-loc[:,i+1,:])-(loc[:,i+1,:]-loc[:,i+2,:])))
    loss = tf.concat(loss_all, 0)
    return tf.reduce_mean(loss)

def cls_loss(group_cls, label):
    scores = tf.nn.softmax(group_cls, axis=3)
    factor = tf.pow(1. - scores, 2)
    scores2 = tf.nn.log_softmax(group_cls, axis=3)
    log_score = 0. - factor * scores2

    batch, rows, lanes, num_cls = group_cls.get_shape()
    label_oh = tf.one_hot(label[:, :, :, 0], num_cls)
    nllloss1 = tf.multiply(label_oh, log_score)
    index = tf.where(nllloss1 > 0)
    nllloss = tf.gather_nd(nllloss1, index)

    cls = tf.reduce_mean(nllloss)

    return cls
