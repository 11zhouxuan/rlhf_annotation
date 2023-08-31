import random


def generate_random_str(
  num=8,
  alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
  ):
  return "".join(random.sample(alphabet,num))



