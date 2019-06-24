#! /usr/bin/env python3

class TypeImporter():
	def __init__(self, key, rule, value, component):
		self.errors = []
		self.key = key
		self.original = self.value = value
		self.rule = rule

		self.init_type_importer(component)


	def init_type_importer(self, component):
		raise NotImplementedError


	def has_errors(self):
		return bool(self.errors)


	def valid(self):
		raise NotImplementedError


	def load_component(self, component, default, *args):
		for key in args:
			setattr(self, key, component.get(key, default))

	def append_error(self, prompt, *args):
		err = prompt.format(*args)
		self.errors.append(err)


	def validate_reject(self):
		for reject in self.reject:
			local = {
				'this': self.value
			}

			if eval(reject, {}, local):
				self.append_error(
					"{}['{}'] ({}): was '{}', now '{}', rejected by '{}'",
					self.key,
					self.rule, 
					self.type, 
					self.original, 
					self.value, 
					reject)

				return False

		return True
