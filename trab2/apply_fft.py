import argparse, cv2, os
from matplotlib import pyplot as plt

from utils import apply_freq_filter

parser = argparse.ArgumentParser()
parser.add_argument("--image", help="Caminho para a imagem.")
parser.add_argument("--r1", type=int,help="Raio r1 para os filtros \
passa-baixa ou passa-alta (para o filtro passa-\
alta, usar também o argumento 'passa-alta').")
parser.add_argument("--r2", type=int, required=False,
                    help="Raio r2 para os filtros passa-faixa \
                          ou rejeita-faixa (para o filtro rejeita-\
                          faixa, usar também o argumento 'rejeita-\
                          faixa').")
parser.add_argument("--passa-alta", action="store_true",
                    help="Booleano para utilizar filtro passa-\
                          alta.")
parser.add_argument("--rejeita-faixa", action="store_true",
                    help="Booleano para utilizar filtro rejeita-\
                          faixa.")
parser.add_argument("--limiar", type=int, required=False,
                    help="Limiar para compressão.")


args = parser.parse_args()

if args.r2 is not None and args.passa_alta:
    print("Raio r2 e argumento --passa-alta passsados, como a implementação considera \
apenas o filtro passa-alta OU os filtro passa-faixa e rejeita faixa, o argumento --passa\
-alta será alterado para 'False'.")
    args.passa_alta = False
if args.passa_alta and args.rejeita_faixa:
    if args.r2 is None:
        print("Ambos os argumentos --passa-alta e --rejeita-faixa foram utilizados, \
como o argumento r2 não foi utilizado, o argumento --rejeita-faixa \
será configurado para 'False'.")
        args.rejeita_faixa = False
    else:
        print("Ambos os argumentos --passa-alta e --rejeita-faixa foram utilizados, \
como o argumento r2 foi utilizado, o argumento --passa-alta \
será configurado para 'False'.")
        args.passa_alta = False
if args.rejeita_faixa:
    assert args.rejeita_faixa and args.r2 is not None, "Caso deseje utilizar o filtro rejeita \
faixa, o argumento r2 deve ser utilizado."

if args.r2 is not None:
        assert args.r2 > args.r1, "r2 deve ser maior que r1."

img_path = args.image
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

filtered, mag, core, compressed = apply_freq_filter(img, args.r1, args.r2,
                                                    args.passa_alta, args.rejeita_faixa,
                                                    args.limiar)

filter_type = "passa_alta" if args.passa_alta else "passa_baixa"
if args.r2 is not None: filter_type = "passa_faixa"
if args.r2 is not None and args.rejeita_faixa: filter_type = "rejeita_faixa"
radius = f"r1={args.r1}" if args.r2 is None else f"r1={args.r1}-r2{args.r2}"
file_path = f"{img_path.split('/')[-1].split('.png')[0]}-{filter_type}-{radius}"

if not os.path.exists("resultados"):
    os.mkdir("resultados")
file_path = "resultados/" + file_path

cv2.imwrite(file_path + ".png", filtered)
cv2.imwrite(file_path + "-espectro.png", mag)
cv2.imwrite(file_path + "-núcleo.png", core)
if compressed is not None:
    cv2.imwrite(file_path + f"-comprimida-limiar={args.limiar}.png", compressed)

    fig, ax = plt.subplots(figsize=(5,3))
    hist_orig = ax.hist(img.ravel(), 256, [0,256])
    fig.savefig(f"{file_path}_originalHistogram.png", bbox_inches='tight')

    fig, ax = plt.subplots(figsize=(5,3))
    hist_orig = ax.hist(compressed.ravel(), 256, [0,256])
    fig.savefig(f"{file_path}_compressedHistogram-threshold={args.limiar}.png", bbox_inches='tight')