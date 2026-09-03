"""E28 (doc 28 §7): ReativoEnxuto — o Reativo sem os 12 pesos mortos (NP = NF+6).
Comportamento identico ao Reativo com os pesos mortos zerados; genoma 44 -> 32 genes.
E23 mostrou que menos genes evoluem mais rapido (3 termos > 26 em G=40)."""
from lab import Reativo, NF

class ReativoEnxuto(Reativo):
    nome = 'reativo-enxuto'; NP = NF + 6
