from ..core import np, auto_grad_logp
from ..utils import logp_var_names, default_start, count
from ..trace import Trace


class Sampler(object):
    # When subclassing, set this to False if grad logp functions aren't needed
    _grad_logp_flag = True

    def __init__(self, logp, grad_logp=None, start=None, scale=1.):
        self.logp = logp
        self.var_names = logp_var_names(logp)
        self.start = default_start(start, logp)
        self.state = self.start
        self.scale = scale*np.ones(len(self.var_names))
        self.sampler = None
        self._sampled = 0
        self._accepted = 0
        if self._grad_logp_flag and grad_logp is None:
            self.grad_logp = auto_grad_logp(logp)
        else:
            if len(self.var_names) > 1 and len(grad_logp) != len(var_names):
                raise TypeError("grad_logp must be iterable with length equal to"
                                " the number of parameters in logp.")
            else:
                self.grad_logp = grad_logp

    def step(self):
        pass

    def sample(self, num, burn=-1, thin=1):
        if self.sampler is None:
            self.sampler = (self.step() for _ in count(start=0, step=1))
        samples = np.array([next(self.sampler) for _ in range(num)])
        trace = samples[burn+1::thin].view(Trace)
        trace.var_names = self.var_names
        return trace

    def reset(self):
        self.state = self.start
        self.sampler = None
        self._accepted = 0
        self._sampled = 0
        return self

    @property
    def acceptance_rate(self):
        return self._accepted/self._sampled