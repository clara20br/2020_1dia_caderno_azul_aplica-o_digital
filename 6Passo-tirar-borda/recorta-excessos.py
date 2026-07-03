"""
Propósito: recortar excessos inferiores das imagens usando a cor preta como referência
Autor: Alexandre Nassar de Peder
Criação: 03/06/2026

OBS: O código analisa de baixo para cima, identifica o ÚLTIMO pixel preto,
sobe 5 pixels e corta tudo abaixo
"""

from PIL import Image
import os
import shutil

def encontrar_ultimo_pixel_preto(imagem, cor_alvo=(0, 0, 0), tolerancia=30):
    """
    Encontra o ÚLTIMO pixel preto de baixo para cima
    Retorna a posição Y do último pixel preto encontrado
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    print(f"Analisando imagem de baixo para cima...")
    print(f"Procurando pelo ÚLTIMO pixel preto (tolerância {tolerancia})")
    
    ultimo_y_preto = None
    ultimo_x_preto = None
    
    # Percorre de baixo para cima
    for y in range(altura - 1, -1, -1):
        encontrou_preto_na_linha = False
        
        # Verifica pixels ao longo da linha
        for x in range(0, largura, 1):  # Verifica todos os pixels
            try:
                pixel = pixels[x, y]
                if len(pixel) == 4:  # RGBA
                    r, g, b, a = pixel
                else:  # RGB
                    r, g, b = pixel[:3]
                
                # Verifica se é preto (próximo do 0)
                if (r < cor_alvo[0] + tolerancia and 
                    g < cor_alvo[1] + tolerancia and 
                    b < cor_alvo[2] + tolerancia):
                    encontrou_preto_na_linha = True
                    ultimo_y_preto = y
                    ultimo_x_preto = x
                    break  # Encontrou um pixel preto nesta linha
            except:
                pass
        
        # Se encontrou um pixel preto nesta linha, registra e continua subindo
        if encontrou_preto_na_linha:
            # Atualiza a posição do último pixel preto
            print(f"  Último pixel preto encontrado em: y={ultimo_y_preto}, x={ultimo_x_preto}")
            
            # Sobe 5 pixels a partir do pixel preto encontrado
            posicao_corte = ultimo_y_preto - 5
            if posicao_corte < 0:
                posicao_corte = 0
            
            # Verifica se a posição de corte é válida
            if posicao_corte > 50:  # Mínimo 50 pixels de altura
                print(f"  Cortando em y={posicao_corte} (5 pixels acima do último pixel preto)")
                return posicao_corte
            else:
                print(f"  Pixel preto encontrado muito perto do topo (y={ultimo_y_preto}), ignorando")
                return None
    
    print("  Nenhum pixel preto encontrado na imagem!")
    return None

def encontrar_linha_branca(imagem, tolerancia=30):
    """
    Método alternativo: procura por linhas totalmente brancas de baixo para cima
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    print("Tentando método alternativo: procurando linhas brancas...")
    
    # Percorre de baixo para cima
    for y in range(altura - 1, -1, -1):
        pixels_brancos = 0
        total_verificados = 0
        
        for x in range(0, largura, 3):
            try:
                pixel = pixels[x, y]
                if len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r, g, b = pixel[:3]
                
                # Verifica se é branco (próximo do 255)
                if (r > 255 - tolerancia and 
                    g > 255 - tolerancia and 
                    b > 255 - tolerancia):
                    pixels_brancos += 1
                total_verificados += 1
            except:
                pass
        
        # Se mais de 80% dos pixels são brancos, é uma linha branca
        if total_verificados > 0 and (pixels_brancos / total_verificados) > 0.8:
            # Encontrou linha branca! Sobe 5 pixels e corta
            posicao_corte = y - 5
            if posicao_corte < 0:
                posicao_corte = 0
            
            if posicao_corte > 50:
                print(f"  Linha branca encontrada em y={y}")
                print(f"  Cortando em y={posicao_corte} (5 pixels acima)")
                return posicao_corte
    
    return None

def encontrar_area_branca_inferior(imagem, tolerancia=30):
    """
    Método alternativo 2: procura por área branca no final da imagem
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    print("Tentando método alternativo 2: procurando área branca...")
    
    # Verifica as últimas 50 linhas
    for y in range(altura - 1, max(0, altura - 100), -1):
        pixels_brancos = 0
        total_verificados = 0
        
        for x in range(0, largura, 5):
            try:
                pixel = pixels[x, y]
                if len(pixel) == 4:
                    r, g, b, a = pixel
                else:
                    r, g, b = pixel[:3]
                
                if (r > 250 and g > 250 and b > 250):
                    pixels_brancos += 1
                total_verificados += 1
            except:
                pass
        
        # Se mais de 95% são brancos, é área branca
        if total_verificados > 0 and (pixels_brancos / total_verificados) > 0.95:
            posicao_corte = y - 5
            if posicao_corte < 0:
                posicao_corte = 0
            
            if posicao_corte > 50:
                print(f"  Área branca encontrada em y={y}")
                print(f"  Cortando em y={posicao_corte} (5 pixels acima)")
                return posicao_corte
    
    return None

def processar_imagens(pasta_origem, pasta_destino):
    """
    Processa todas as imagens da pasta origem, recortando as que têm excessos inferiores
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    if not arquivos:
        print(f"Nenhum arquivo de imagem encontrado na pasta '{pasta_origem}'")
        return
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    imagens_recortadas = 0
    imagens_copiadas = 0
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\n{'='*60}")
                print(f"Processando: {arquivo} ({imagem.width}x{imagem.height})")
                print(f"{'='*60}")
                
                # Primeiro tenta encontrar o último pixel preto
                posicao_corte = encontrar_ultimo_pixel_preto(imagem)
                
                # Se não encontrou, tenta métodos alternativos
                if posicao_corte is None:
                    posicao_corte = encontrar_linha_branca(imagem)
                
                if posicao_corte is None:
                    posicao_corte = encontrar_area_branca_inferior(imagem)
                
                if posicao_corte is not None and posicao_corte > 0:
                    # Recorta a imagem
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                    imagens_recortadas += 1
                else:
                    # Se não encontrou nada, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem excesso detectado)")
                    imagens_copiadas += 1
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
                imagens_copiadas += 1
            except:
                print(f"✗ Não foi possível copiar o arquivo")
    
    print(f"\n{'='*60}")
    print("RESUMO DO PROCESSAMENTO")
    print(f"{'='*60}")
    print(f"  - Imagens recortadas: {imagens_recortadas}")
    print(f"  - Imagens copiadas: {imagens_copiadas}")
    print(f"  - Total processado: {len(arquivos)}")

def processar_imagem_individual(caminho_imagem, pasta_destino):
    """
    Processa uma única imagem e salva na pasta destino
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    try:
        with Image.open(caminho_imagem) as imagem:
            print(f"\n{'='*60}")
            print(f"Processando: {os.path.basename(caminho_imagem)} ({imagem.width}x{imagem.height})")
            print(f"{'='*60}")
            
            # Primeiro tenta encontrar o último pixel preto
            posicao_corte = encontrar_ultimo_pixel_preto(imagem)
            
            # Se não encontrou, tenta métodos alternativos
            if posicao_corte is None:
                posicao_corte = encontrar_linha_branca(imagem)
            
            if posicao_corte is None:
                posicao_corte = encontrar_area_branca_inferior(imagem)
            
            if posicao_corte is not None and posicao_corte > 0:
                # Recorta a imagem
                area_corte = (0, 0, imagem.width, posicao_corte)
                imagem_recortada = imagem.crop(area_corte)
                
                nome_base = os.path.splitext(os.path.basename(caminho_imagem))[0]
                caminho_destino = os.path.join(pasta_destino, f"{nome_base}_recortado.png")
                
                imagem_recortada.save(caminho_destino)
                print(f"✓ Imagem recortada salva como: {caminho_destino}")
                print(f"  Tamanho: {imagem_recortada.width}x{imagem_recortada.height}")
                return caminho_destino
            else:
                print(f"✓ Nenhum excesso encontrado na imagem")
                return None
                
    except Exception as e:
        print(f"✗ Erro ao processar imagem: {e}")
        return None

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "inteiras_separadas"  # Pasta com as imagens a serem processadas
    pasta_destino = "finalizadas"  # Pasta onde serão salvas as imagens processadas
    
    print("="*60)
    print("RECORTANDO EXCESSOS INFERIORES DAS IMAGENS")
    print("="*60)
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print("\nCritérios:")
    print("  1. Procurar pelo ÚLTIMO pixel preto de baixo para cima")
    print("  2. Quando encontrar, subir 5 pixels")
    print("  3. Cortar tudo abaixo")
    print("  4. Se não encontrar pixels pretos, tentar métodos alternativos")
    print("="*60)
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"\nErro: A pasta '{pasta_origem}' não existe!")
        print("Verifique o caminho e tente novamente.")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino)
    
    print("\n" + "="*60)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")
    print("="*60)