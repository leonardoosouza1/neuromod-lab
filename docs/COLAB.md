# Rodar no Colab

## Setup rápido

Notebook novo → **Runtime → Alterar tipo de ambiente → GPU (T4 ou melhor)**.

```python
# célula 1
!pip install -q torch numpy
from google.colab import drive; drive.mount('/content/drive')
!mkdir -p /content/drive/MyDrive/neuromod-lab
%cd /content/drive/MyDrive/neuromod-lab
```

Descompacte o zip nessa pasta e depois:

```python
# célula 2
!python src/rodar.py --perito
```

```python
# célula 3 — só se o portão passar
!python src/rodar.py --bateria -P 8192 -G 100 -R 8
```

## Dimensionamento de VRAM

Medido em T4 (15.6 GB), com 8 cidades e `R=8`:

```
P = 2048    →  0.4 GB
P = 8192    →  1.6 GB
P = 32768   →  6.2 GB
P = 57000   →  ~11 GB   (teto prático)
```

A memória escala linear com `P × cidades × R`. O `--bateria` mede o pico com a
configuração real antes de começar e aborta com sugestão se não couber.

## O gargalo não é a GPU

Os tensores são pequenos (`(B, 26)`), então a GPU nunca enche de trabalho — o
custo é o **laço sequencial de T passos** lançando kernels minúsculos. Por isso:

- subir `P` é quase de graça (mesmo tempo por geração)
- subir `T` custa proporcionalmente
- `torch.compile` daria 2-3×, mas recompila se houver contador Python no `passo`

Consequência prática: **use o batch para réplicas, não só para população**. Com
`R=8` cada genoma é avaliado em 64 mundos e o fitness tem erro 8× menor. Isso
vale mais que população gigante com fitness ruidoso.

## Limpar a GPU depois de interromper

```python
import gc, torch
def limpar_gpu():
    alvos = []
    for obj in gc.get_objects():
        try:
            d = getattr(obj, '__dict__', None)
            if isinstance(d, dict) and any(torch.is_tensor(v) and v.is_cuda for v in d.values()):
                alvos.append(obj)
        except Exception: pass
    for obj in alvos:
        try:
            for k in [k for k,v in list(obj.__dict__.items())
                      if torch.is_tensor(v) and v.is_cuda]:
                delattr(obj, k)
        except Exception: pass
    for k in [k for k,v in list(globals().items())
              if torch.is_tensor(v) and getattr(v,'is_cuda',False)]:
        del globals()[k]
    try:
        ip = get_ipython()
        for k in list(ip.user_ns.get('Out', {})): ip.user_ns['Out'].pop(k, None)
        ip.history_manager.reset()
    except Exception: pass
    for _ in range(3):
        gc.collect(); torch.cuda.empty_cache(); torch.cuda.ipc_collect()
    torch.cuda.reset_peak_memory_stats()
    a = torch.cuda.memory_allocated()/1e9; r = torch.cuda.memory_reserved()/1e9
    t = torch.cuda.get_device_properties(0).total_memory/1e9
    print(f'alocado {a:.2f} | reservado {r:.2f} | livre {t-r:.2f} de {t:.1f} GB')
limpar_gpu()
```

O que segura memória com mais frequência são os objetos `Lote` presos em atributos
de instância — por isso a função apaga atributos, não só variáveis globais.

Se `alocado` continuar acima de 0.5 GB, é **Runtime → Reiniciar sessão**.

## Armadilhas conhecidas

| Sintoma | Causa |
|---|---|
| `NameError: DEV` | runtime reiniciou; rode a célula de setup de novo |
| `recompile_limit (8)` no dynamo | contador Python dentro da função compilada |
| VRAM não libera ao interromper | `Lote` preso em atributo de objeto |
| Log não aparece | `print = functools.partial(print, flush=True)` |
| Sessão cai sem erro | `mode='reduce-overhead'` no compile com shapes variáveis |
