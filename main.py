import random
import matplotlib.pyplot as plt
import numpy as np

# Gerador de referências com distribuição Gaussiana (Normal)
def gerar_referencias_gaussiana_ciclica(processos, max_paginas, tamanho_fase, fases_por_processo, ciclos):
    sequencias = []
    desvio = 0

    for _ in range(processos):
        fases_fixas = []

        for _ in range(fases_por_processo):
            media = random.randint(0, max_paginas - 1)
            desvio += 3
            fase = np.random.normal(loc=media, scale=desvio, size=tamanho_fase)
            fase = np.clip(np.round(fase), 0, max_paginas - 1).astype(int).tolist()
            fases_fixas.append(fase)

        referencias = []
        for _ in range(ciclos):
            for fase in fases_fixas:
                referencias.extend(fase)

        sequencias.append(referencias)

    return sequencias

# Algoritmo FIFO
def fifo(referencias, molduras):
    memoria = []
    faltas = 0
    for pagina in referencias:
        if pagina not in memoria:
            faltas += 1
            if len(memoria) < molduras:
                memoria.append(pagina)
            else:
                memoria.pop(0)
                memoria.append(pagina)
    return faltas

# Algoritmo de Envelhecimento
def envelhecimento(referencias, molduras, bits=8):
    memoria = {}
    contador = {}
    faltas = 0

    for pagina in referencias:
        for p in contador:
            contador[p] >>= 1

        if pagina in memoria:
            contador[pagina] |= 1 << (bits - 1)
        else:
            faltas += 1
            if len(memoria) < molduras:
                memoria[pagina] = True
                contador[pagina] = 1 << (bits - 1)
            else:
                menos_usada = min(contador, key=contador.get)
                del memoria[menos_usada]
                del contador[menos_usada]
                memoria[pagina] = True
                contador[pagina] = 1 << (bits - 1)
    return faltas

def simular():
    processos = 3
    max_paginas = 30
    tamanho_fase = 50
    fases_por_processo = 8
    ciclos = 4
    molduras_teste = list(range(5, 31, 5))
    total_referencias = fases_por_processo * tamanho_fase * ciclos

    sequencias = gerar_referencias_gaussiana_ciclica(processos, max_paginas, tamanho_fase, fases_por_processo, ciclos)

    with open("referencias_gaussiana.txt", "w") as f:
        for i, seq in enumerate(sequencias):
            f.write(f"Processo {i+1}: {seq}\n")

    todos_resultados = []

    for i, seq in enumerate(sequencias):
        fifo_resultado = []
        envelhecimento_resultado = []

        for m in molduras_teste:
            faltas_fifo = fifo(seq, m)
            faltas_envelhecimento = envelhecimento(seq, m)
            fifo_resultado.append(faltas_fifo / (len(seq) / 1000))
            envelhecimento_resultado.append(faltas_envelhecimento / (len(seq) / 1000))

        todos_resultados.append((fifo_resultado, envelhecimento_resultado))

        plt.figure()
        plt.plot(molduras_teste, fifo_resultado, label="FIFO", marker='o')
        plt.plot(molduras_teste, envelhecimento_resultado, label="Envelhecimento", linestyle="--", marker='x')
        plt.xlabel("Número de Molduras de Página")
        plt.ylabel(f"Faltas por {total_referencias} Referências")
        plt.title(f"Processo {i+1}: FIFO x Envelhecimento")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"grafico_processo_{i+1}.png")
        plt.show()

    plt.figure()
    for i, (fifo_resultado, envelhecimento_resultado) in enumerate(todos_resultados):
        plt.plot(molduras_teste, fifo_resultado, label=f"FIFO - Processo {i+1}", marker='o')
        plt.plot(molduras_teste, envelhecimento_resultado, label=f"Envelhecimento - Processo {i+1}", linestyle="--", marker='x')

    plt.xlabel("Número de Molduras de Página")
    plt.ylabel("Faltas por 1000 Referências")
    plt.title("Comparação Geral - FIFO x Envelhecimento")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("grafico_geral.png")
    plt.show()

if __name__ == "__main__":
    simular()
