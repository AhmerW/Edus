from pickle import dumps

class CustomCache(object):
	def __init__(self, func):
		self.func = func
		self.rvs = {}

	def __call__(self, *args, **kwargs):
		paras = (dumps(args), dumps(kwargs))
		if paras in self.rvs:
			return self.rvs[paras]
		out = self.func(*args, **kwargs)
		self.rvs[paras] = out
		return out
