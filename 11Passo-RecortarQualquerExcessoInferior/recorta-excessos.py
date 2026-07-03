"""
Propósito: recortar excessos inferiores que possam ter ficado nas imagens, usando a cor preta como referência
Autor: Alexandre Nassar de Peder
Criação: 02/10/2025
Atualização: 03/06/2026

OBS: este código vai percorrer a imagem de baixo para cima, procurando pelo último pixel preto (RGB 0,0,0).
Quando encontrar, vai recortar 5 pixels acima desse ponto, eliminando tudo que está abaixo.
"""

from PIL import Image
import os
import shutil

def encontrar_ultimo_pixel_preto(imagem, cor_alvo, tolerancia=10):
    """
    Percorre a imagem de baixo para cima procurando pelo último pixel da cor preta
    Retorna a posição Y onde deve ser feito o corte (5 pixels acima do último pixel preto)
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    ultimo_y_preto = -1
    
    # Percorre a imagem de baixo para cima (começa do fundo)
    for y in range(altura - 1, -1, -1):
        # Verifica todos os pixels nesta linha horizontal
        for x in range(largura):
            pixel = pixels[x, y]
            
            # Extrai os valores RGB (ignorando o canal alpha se existir)
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se o pixel está próximo da cor preta (dentro da tolerância)
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                ultimo_y_preto = y
                print(f"Último pixel preto encontrado na linha y={y}, posição x={x}")
                # Como queremos o último pixel preto (mais próximo do fundo),
                # continuamos procurando nas linhas acima
                break  # Sai do loop for x, mas continua com o próximo y
        
        # Se encontrou um pixel preto, já podemos sair do loop y
        # porque estamos percorrendo de baixo para cima
        if ultimo_y_preto != -1:
            break
    
    if ultimo_y_preto != -1:
        # Recorta 5 pixels acima do último pixel preto
        posicao_corte = ultimo_y_preto - 5
        if posicao_corte < 0:
            posicao_corte = 0
        print(f"Posição de corte: y={posicao_corte} (último preto em y={ultimo_y_preto} - 5 pixels)")
        return posicao_corte
    else:
        print("Nenhum pixel preto encontrado na imagem")
        return None

def processar_imagens(pasta_origem, pasta_destino):
    """
    Processa todas as imagens da pasta origem, recortando as que têm pixels pretos
    e copiando todas para a pasta destino
    """
    # Cria a pasta de destino se não existir
    os.makedirs(pasta_destino, exist_ok=True)
    
    # Lista todos os arquivos da pasta origem
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    # Contadores para estatísticas
    imagens_com_corte = 0
    imagens_sem_corte = 0
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            # Abre a imagem
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                # Procura pelo último pixel preto
                posicao_corte = encontrar_ultimo_pixel_preto(imagem, (0, 0, 0))
                
                if posicao_corte is not None and posicao_corte > 0 and posicao_corte < imagem.height:
                    # Se encontrou pixel preto, recorta a imagem
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                    imagens_com_corte += 1
                else:
                    # Se não encontrou pixel preto, copia a imagem original
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem pixels pretos detectados)")
                    imagens_sem_corte += 1
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            # Tenta copiar o arquivo mesmo com erro
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
                imagens_sem_corte += 1
            except:
                print(f"✗ Não foi possível copiar o arquivo")
    
    # Resumo final
    print("\n" + "="*50)
    print(f"RESUMO DO PROCESSAMENTO:")
    print(f"Total de imagens processadas: {len(arquivos)}")
    print(f"Imagens com corte: {imagens_com_corte}")
    print(f"Imagens sem corte: {imagens_sem_corte}")

# Função principal
if __name__ == "__main__":
    # Configurações
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    
    print("Iniciando processamento de imagens...")
    print("Analisando de baixo para cima em busca de pixels pretos...")
    print(f"Pasta origem: {pasta_origem}")
    print(f"Pasta destino: {pasta_destino}")
    print("Cor alvo: PRETO (RGB 0,0,0)")
    print("Tolerância: 10 (para capturar variações de preto)")
    print("Corte: 5 pixels acima do último pixel preto")
    
    # Verifica se a pasta origem existe
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        print("Certifique-se de que a pasta 'questoes' do passo 10 foi copiada para este diretório.")
        exit(1)
    
    # Executa o processamento
    processar_imagens(pasta_origem, pasta_destino)
    
    print("\n" + "="*50)
    print("Processamento concluído!")
    print(f"Todas as imagens foram salvas em: {pasta_destino}")
    print("\n" + "="*50)
    print("IMPORTANTE: Verifique visualmente as imagens para confirmar se os cortes foram feitos corretamente.")
    print("Se algum corte estiver incorreto, ajuste a posição de corte e execute novamente.")