import numpy as np


class KalmanFilter:

    def __init__(self, x0=np.array([0] * 10), var0=0.001, q=0.01, r=0.1):
        self.x_curr = np.array(x0)
        self.var_curr = var0
        self.q = q
        self.r = r

    def update(self, observation, time_difference):
        observation = np.array(observation)
        x_predict = self.x_curr

        var_predict = self.var_curr + self.q * np.sqrt(time_difference)

        kalman_gain = var_predict / (var_predict + self.r)

        self.x_curr = x_predict + kalman_gain * (observation - x_predict)
        self.var_curr = kalman_gain * self.r

        return self.x_curr, self.var_curr
