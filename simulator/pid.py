__author__ = 'will'


class PID:
    """
    Discrete PID control
    """

    def __init__(self, p=2.0, i=0.0, d=1.0, integrator_max=500, integrator_min=-500, usetime=False):

        self.kp = p
        self.ki = i
        self.kd = d
        self.derivator = 0
        self.integrator = 0
        self.integrator_max = integrator_max
        self.integrator_min = integrator_min

        self.set_point = 0.0
        self.error = 0.0
        self.lasterror = 0.0

        self.usetime = usetime

    def update(self, current_value=0, error=None):
        """
        Calculate PID output value for given reference input and feedback
        """

        if error is not None:
            self.error = error
        else:
            self.error = self.set_point - current_value

        self.derivator = self.error - self.lasterror

        self.integrator = max(min(self.integrator + self.error, self.integrator_max), self.integrator_min)

        if self.usetime:
            PID = self.kp * (self.error + self.derivator / self.kd + self.integrator / self.ki)
        else:
            PID = self.kp * self.error + self.ki * self.integrator + self.kd * self.derivator

        return PID

    def setPoint(self, set_point):
        """
        Initilize the setpoint of PID
        """
        self.set_point = set_point
        # self.Integrator = 0
        # self.Derivator = 0

    def setIntegrator(self, Integrator):
        self.Integrator = Integrator

    def setDerivator(self, Derivator):
        self.Derivator = Derivator

    def setKp(self, P):
        self.Kp = P

    def setKi(self, I):
        self.Ki = I

    def setKd(self, D):
        self.Kd = D

    def getPoint(self):
        return self.set_point

    def getError(self):
        return self.error

    def getIntegrator(self):
        return self.Integrator

    def getDerivator(self):
        return self.Derivator