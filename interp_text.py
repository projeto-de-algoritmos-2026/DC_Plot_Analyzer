def interp_text(tau):
    if tau > 0.8:  return "Sequência quase perfeitamente ordenada."
    if tau > 0.4:  return "Correlação positiva moderada."
    if tau > -0.4: return "Correlação fraca — próxima ao aleatório."
    if tau > -0.8: return "Correlação negativa moderada."
    return "Sequência quase em ordem inversa."