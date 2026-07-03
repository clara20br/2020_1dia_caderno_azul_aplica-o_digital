"""
Propósito: concatenas verticalmente as imagens de cada pasta vinda do passo 5
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a pasta "divididas-sem-bordas-do-meio" do passo 5 para essa pasta do passo 6

OBS2: o objetivo deste passo é pegar as colunas já recortadas e empilhar uma em cima da outra, na ordem correta, para formar uma única imagem final. Futuramente, essa imagem concatenada será dividida em imagens de cada questão, mas isso será feito no passo 7.

OBS3: este código vai criar uma imagem final chamada "colunas_concatenadas_verticalmente.png" que vai ter todas as colunas concatenadas verticalmente na ordem correta

OBS4: não compensa concatenar as páginas inteiras. Tenha isso em mente para o passo 7. Concatene apenas as colunas.

OBS5: tem provas que as colunas são de tamanhos diferentes. Tenha isso em mente. Não ajuda muito ter uma coluna maior que a outra. Se esse for o seu caso, você pode ajustar o código para lidar com isso, tal como concatenar as colunas do mesmo tamanho e depois concatenar as colunas menores em outra imagem. Mas isso é um caso específico. Se precisar, coloque as colunas do mesmo tamanho em uma única pasta, e execute atualizando as linhas 24 e 60

OBS6: execute o código
"""
"""
Propósito: concatenar verticalmente as imagens de cada pasta vinda do passo 5
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS1: puxe a pasta "divididas-sem-bordas-do-meio" do passo 5 para essa pasta do passo 6

OBS2: o objetivo deste passo é pegar as colunas já recortadas e empilhar uma em cima da outra, na ordem correta, para formar uma única imagem final. Futuramente, essa imagem concatenada será dividida em imagens de cada questão, mas isso será feito no passo 7.

OBS3: este código vai criar uma imagem final chamada "colunas_concatenadas_verticalmente.png" que vai ter todas as colunas concatenadas verticalmente na ordem correta
"""

from PIL import Image
import os
import re

pasta_imagens = "inteiras_separadas"
pasta_saida = "."
os.makedirs(pasta_saida, exist_ok=True)

# Função para extrair o número da página e ordenar corretamente
def get_sort_key(nome_arquivo):
    """
    Extrai o número da página e o lado para ordenação
    Suporta diferentes formatos:
    - pagina_enem_41_esquerda.png
    - pagina_enem_41_direita.png
    - pagina_enem_41.png
    - pagina_41.png
    """
    # Tenta encontrar o número da página em diferentes padrões
    padroes = [
        r'pagina_enem_(\d+)_',  # pagina_enem_41_
        r'pagina_enem_(\d+)\.',  # pagina_enem_41.png
        r'pagina_(\d+)_',  # pagina_41_
        r'pagina_(\d+)\.',  # pagina_41.png
        r'_(\d+)_',  # _41_
        r'_(\d+)\.',  # _41.png
    ]
    
    numero = None
    for padrao in padroes:
        match = re.search(padrao, nome_arquivo)
        if match:
            numero = int(match.group(1))
            break
    
    # Se não encontrar número, usa 0 como fallback
    if numero is None:
        print(f"AVISO: Não foi possível extrair número de: {nome_arquivo}")
        numero = 0
    
    # Define a ordem: esquerda primeiro (0), depois direita (1)
    if 'esquerda' in nome_arquivo.lower():
        lado = 0
    elif 'direita' in nome_arquivo.lower() or 'direito' in nome_arquivo.lower():
        lado = 1
    else:
        # Se não tem lado especificado, tenta extrair do nome
        # ou usa 0 por padrão
        lado = 0
    
    return (numero, lado)

# Pegar e ordenar as imagens corretamente
print(f"Verificando pasta: {pasta_imagens}")
arquivos = [f for f in os.listdir(pasta_imagens) if f.endswith('.png')]

if not arquivos:
    print(f"ERRO: Nenhum arquivo PNG encontrado na pasta '{pasta_imagens}'")
    print("Verifique se a pasta existe e contém imagens.")
    exit()

print(f"Encontrados {len(arquivos)} arquivos PNG")

# Ordenar os arquivos
try:
    arquivos.sort(key=get_sort_key)
    print("Arquivos ordenados com sucesso!")
except Exception as e:
    print(f"Erro ao ordenar: {e}")
    print("Usando ordenação alfabética como fallback...")
    arquivos.sort()

# Mostrar a ordem dos arquivos
print("\nOrdem dos arquivos:")
for i, arquivo in enumerate(arquivos):
    print(f"  {i+1}. {arquivo}")

# Abrir todas as imagens na ordem correta
imagens = []
alturas = []
larguras = []

print("\nAbrindo imagens...")
for arquivo in arquivos:
    caminho = os.path.join(pasta_imagens, arquivo)
    try:
        img = Image.open(caminho)
        imagens.append(img)
        alturas.append(img.height)
        larguras.append(img.width)
        print(f"  {arquivo}: {img.width}x{img.height}")
    except Exception as e:
        print(f"  ERRO ao abrir {arquivo}: {e}")

if not imagens:
    print("Nenhuma imagem foi carregada!")
    exit()

# Encontrar a largura máxima
largura_max = max(larguras)
print(f"\nLargura máxima: {largura_max}")

# Concatenar verticalmente
altura_total = sum(alturas)
print(f"Altura total: {altura_total}")

print("\nConcatenando imagens...")
imagem_final = Image.new('RGB', (largura_max, altura_total))

y = 0
for i, img in enumerate(imagens):
    # Centraliza a imagem horizontalmente se for menor que a largura máxima
    x_offset = (largura_max - img.width) // 2
    imagem_final.paste(img, (x_offset, y))
    print(f"  Colocando imagem {i+1} em y={y}")
    y += img.height

# Salvar
caminho_saida = os.path.join(pasta_saida, 'colunas_concatenadas_verticalmente.png')
imagem_final.save(caminho_saida)
print(f"\nImagem final salva como: {caminho_saida}")
print(f"Tamanho final: {largura_max}x{altura_total}")
print(f"Total de imagens concatenadas: {len(imagens)}")