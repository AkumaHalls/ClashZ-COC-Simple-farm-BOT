import pyautogui
import cv2
import numpy as np
import time
import os
from PIL import ImageGrab, Image # Adicionado Image para salvar o template

# --- Configurações Iniciais ---
IMAGE_DIR = "imagens"
DEBUG_IMAGE_DIR = "imagens_debug" # Pasta para salvar screenshots de depuração
DEBUG_MODE = True # Mude para False para desativar o salvamento de imagens de depuração

# Nomes dos arquivos de imagem
IMG_ATACAR_VILA = os.path.join(IMAGE_DIR, "atacar_vila.png")
IMG_BUSCAR_AGORA = os.path.join(IMAGE_DIR, "buscar_agora.png")
IMG_SUPER_GOBLIN = os.path.join(IMAGE_DIR, "super_goblin.png")
IMG_ENCERRAR_BATALHA = os.path.join(IMAGE_DIR, "encerrar_batalha.png")
IMG_CONFIRMAR_ENCERRAR = os.path.join(IMAGE_DIR, "confirmar_encerrar.png")
IMG_RETORNAR_BASE = os.path.join(IMAGE_DIR, "retornar_base.png")

# --- CONFIGURAÇÃO DA ÁREA DE DEPLOY DE TROPAS ---
# Se DEPLOYMENT_AREA_RECT for deixado como None, o script tentará calcular
# uma área automaticamente baseada no tamanho da tela.
# Você ainda pode definir manualmente se precisar de mais precisão:
# Formato: (x_canto_superior_esquerdo, y_canto_superior_esquerdo, largura_retangulo, altura_retangulo)
# Exemplo: DEPLOYMENT_AREA_RECT = (200, 150, 600, 500)
DEPLOYMENT_AREA_RECT = None

# Porcentagens da tela para definir a área de deploy automática (se DEPLOYMENT_AREA_RECT for None)
# Ex: 0.15 significa 15% de margem de cada lado.
AUTO_DEPLOY_MARGIN_X_PERCENT = 0.18 # Margem horizontal (18% de cada lado)
AUTO_DEPLOY_MARGIN_Y_PERCENT = 0.22 # Margem vertical (22% de cada lado)


# --- Funções Auxiliares ---

def ensure_debug_dir():
    """Garante que o diretório de imagens de depuração exista."""
    if DEBUG_MODE and not os.path.exists(DEBUG_IMAGE_DIR):
        os.makedirs(DEBUG_IMAGE_DIR)

def find_image_on_screen(template_image_path, confidence=0.8, region=None):
    """
    Encontra uma imagem (template) na tela e retorna as coordenadas do centro.
    'region' é uma tupla opcional (left, top, width, height) para limitar a área de busca.
    """
    ensure_debug_dir()
    base_template_name = os.path.basename(template_image_path)

    if not os.path.exists(template_image_path):
        print(f"[ERRO] Imagem não encontrada no caminho: {template_image_path}")
        return None
    try:
        screen_pil = None
        if region:
            screen_pil = ImageGrab.grab(bbox=region)
            if DEBUG_MODE:
                try: # Adicionado try-except para salvar screenshot da região
                    screen_pil.save(os.path.join(DEBUG_IMAGE_DIR, f"debug_screenshot_region_{base_template_name}"))
                except Exception as e_save_region:
                    print(f"[AVISO_DEBUG] Não foi possível salvar screenshot da região: {e_save_region}")
        else:
            screen_pil = ImageGrab.grab()
            # Não salvar screenshot completo aqui para evitar excesso, salvo em caso de falha

        screen_np = np.array(screen_pil)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_BGR2GRAY)

        template_cv = cv2.imread(template_image_path, 0)
        if template_cv is None:
            print(f"[ERRO] Não foi possível carregar o template OpenCV: {template_image_path}")
            return None
        
        if DEBUG_MODE: 
            try:
                cv2.imwrite(os.path.join(DEBUG_IMAGE_DIR, f"debug_template_{base_template_name}"), template_cv)
            except Exception as e_save_template:
                print(f"[AVISO_DEBUG] Não foi possível salvar a imagem do template de depuração: {e_save_template}")


        w, h = template_cv.shape[::-1]
        res = cv2.matchTemplate(screen_gray, template_cv, cv2.TM_CCOEFF_NORMED)
        
        # Encontra o local com a maior confiança
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= confidence:
            pt = max_loc # Ponto de maior confiança
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            
            if region:
                center_x += region[0]
                center_y += region[1]

            print(f"[INFO] Imagem '{base_template_name}' encontrada em: ({center_x}, {center_y}) com confiança: {max_val:.2f} (requerido: {confidence:.2f})")
            return (center_x, center_y)
        else:
            if DEBUG_MODE:
                print(f"[DEBUG] Imagem '{base_template_name}' NÃO encontrada. Confiança máxima: {max_val:.2f} (requerido: {confidence:.2f}). Salvando screenshot para análise.")
                debug_screenshot_path = os.path.join(DEBUG_IMAGE_DIR, f"debug_screenshot_FAIL_{base_template_name}")
                # Salva o screenshot que foi usado para a busca (seja região ou tela inteira)
                screen_pil.save(debug_screenshot_path)
                print(f"[DEBUG] Screenshot salvo em: {debug_screenshot_path}")
                print(f"[DEBUG] Template usado (salvo em debug): debug_template_{base_template_name}")
                print(f"[DICA_DEBUG] Verifique '{debug_screenshot_path}' e compare com 'debug_template_{base_template_name}'.")
                print(f"[DICA_DEBUG] A imagem na tela corresponde? O 'confidence' ({confidence}) está adequado?")
            return None
        
    except Exception as e:
        print(f"[ERRO] em find_image_on_screen para '{template_image_path}': {e}")
        if DEBUG_MODE:
            print(f"[DICA_DEBUG] Verifique se o LDPlayer está visível e não obstruído.")
        return None

def click_on_image(image_path, confidence=0.8, duration=0.1, region=None, clicks=1, interval=0.1):
    coords = find_image_on_screen(image_path, confidence, region)
    if coords:
        pyautogui.moveTo(coords[0], coords[1], duration=duration)
        pyautogui.click(clicks=clicks, interval=interval)
        print(f"[INFO] Clicado em '{os.path.basename(image_path)}' em {coords}")
        return True
    else:
        return False

def wait_for_image(image_path, timeout_seconds=10, confidence=0.8, region=None):
    print(f"[INFO] Esperando pela imagem '{os.path.basename(image_path)}' por até {timeout_seconds}s...")
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        coords = find_image_on_screen(image_path, confidence, region)
        if coords:
            print(f"[INFO] Imagem '{os.path.basename(image_path)}' apareceu.")
            return coords
        time.sleep(0.5)
    print(f"[AVISO] Tempo esgotado esperando por '{os.path.basename(image_path)}'.")
    return None

# --- Lógica do Jogo ---

def get_deployment_area_rect():
    """
    Retorna o retângulo da área de deploy.
    Se DEPLOYMENT_AREA_RECT estiver definido manualmente, usa ele.
    Caso contrário, calcula uma área baseada no tamanho da tela.
    """
    global DEPLOYMENT_AREA_RECT # Para poder modificar a variável global se calcularmos automaticamente
    if DEPLOYMENT_AREA_RECT is not None and isinstance(DEPLOYMENT_AREA_RECT, tuple) and len(DEPLOYMENT_AREA_RECT) == 4:
        print(f"[INFO_DEPLOY] Usando área de deploy manual: {DEPLOYMENT_AREA_RECT}")
        return DEPLOYMENT_AREA_RECT

    print("[INFO_DEPLOY] DEPLOYMENT_AREA_RECT não definido manualmente. Calculando área de deploy automática...")
    screen_width, screen_height = pyautogui.size()
    
    margin_x = int(screen_width * AUTO_DEPLOY_MARGIN_X_PERCENT)
    margin_y = int(screen_height * AUTO_DEPLOY_MARGIN_Y_PERCENT)
    
    auto_left = margin_x
    auto_top = margin_y
    auto_width = screen_width - (2 * margin_x)
    auto_height = screen_height - (2 * margin_y)
    
    # Atualiza a variável global para que possa ser usada em outros lugares se necessário,
    # e para que seja impressa no início do script.
    DEPLOYMENT_AREA_RECT = (auto_left, auto_top, auto_width, auto_height)
    print(f"[INFO_DEPLOY] Área de deploy automática calculada: {DEPLOYMENT_AREA_RECT}")
    print(f"[AVISO_DEPLOY] Esta área automática é uma aproximação. Se o deploy não estiver ideal,")
    print(f"               você pode ajustar AUTO_DEPLOY_MARGIN_X_PERCENT e AUTO_DEPLOY_MARGIN_Y_PERCENT no script,")
    print(f"               ou definir DEPLOYMENT_AREA_RECT manualmente para maior precisão.")
    return DEPLOYMENT_AREA_RECT


def deploy_troops(num_total_goblin_clicks=90, points_per_edge=5, delay_per_click=0.05): # Alterado num_total_goblin_clicks para 90
    """
    Seleciona os Super Goblins e os distribui ao longo das bordas da área de deploy
    de forma intercalada para maior simetria.
    """
    print("[AÇÃO] Iniciando deploy de tropas pelas bordas (modo simétrico)...")
    
    current_deployment_area = get_deployment_area_rect()
    if current_deployment_area is None:
        print("[ERRO_DEPLOY] Não foi possível obter a área de deploy.")
        return False

    if not click_on_image(IMG_SUPER_GOBLIN, confidence=0.4):
        print("[ERRO_DEPLOY] Não foi possível selecionar Super Goblin. Abortando deploy.")
        return False
    
    time.sleep(0.3) 

    left, top, width, height = current_deployment_area
    right = left + width
    bottom = top + height
    
    actual_points_per_edge = max(1, points_per_edge) 

    # Listas para armazenar coordenadas de cada borda
    top_coords = []
    right_coords = []
    bottom_coords = []
    left_coords = []

    # Gerar pontos para a borda SUPERIOR
    if actual_points_per_edge == 1:
        top_coords.append({'x': left + width // 2, 'y': top, 'edge': 'top'})
    else:
        step_x = width / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            top_coords.append({'x': left + int(step_x * i), 'y': top, 'edge': 'top'})

    # Gerar pontos para a borda DIREITA
    if actual_points_per_edge == 1:
        right_coords.append({'x': right, 'y': top + height // 2, 'edge': 'right'})
    else:
        step_y = height / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            right_coords.append({'x': right, 'y': top + int(step_y * i), 'edge': 'right'})

    # Gerar pontos para a borda INFERIOR (da direita para a esquerda para variar)
    if actual_points_per_edge == 1:
        bottom_coords.append({'x': left + width // 2, 'y': bottom, 'edge': 'bottom'})
    else:
        step_x = width / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            bottom_coords.append({'x': right - int(step_x * i), 'y': bottom, 'edge': 'bottom'})
            
    # Gerar pontos para a borda ESQUERDA (de baixo para cima para variar)
    if actual_points_per_edge == 1:
        left_coords.append({'x': left, 'y': top + height // 2, 'edge': 'left'})
    else:
        step_y = height / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            left_coords.append({'x': left, 'y': bottom - int(step_y * i), 'edge': 'left'})

    # Intercalar os pontos das bordas para criar a lista final de deploy
    all_deploy_coords_intercalated = []
    max_len = actual_points_per_edge # Todas as listas de borda terão este tamanho
    
    for i in range(max_len):
        if i < len(top_coords):
            all_deploy_coords_intercalated.append(top_coords[i])
        if i < len(right_coords):
            all_deploy_coords_intercalated.append(right_coords[i])
        if i < len(bottom_coords):
            all_deploy_coords_intercalated.append(bottom_coords[i])
        if i < len(left_coords):
            all_deploy_coords_intercalated.append(left_coords[i])
    
    if not all_deploy_coords_intercalated:
        print("[AVISO_DEPLOY] Nenhum ponto de deploy foi gerado. Verifique a configuração da área de deploy.")
        return False

    print(f"[INFO_DEPLOY] Gerados {len(all_deploy_coords_intercalated)} pontos de deploy distintos de forma intercalada.")
    
    # Distribuir os cliques totais entre os pontos gerados
    for i in range(num_total_goblin_clicks):
        # Ciclar pelos pontos de deploy intercalados
        coord_data = all_deploy_coords_intercalated[i % len(all_deploy_coords_intercalated)]
        
        pyautogui.moveTo(coord_data['x'], coord_data['y'], duration=0.02) 
        pyautogui.click()
        # print(f"[AÇÃO_DEPLOY] Goblin {i+1} deployado em ({coord_data['x']},{coord_data['y']}) na borda {coord_data['edge']}") # Descomente para debug detalhado
        time.sleep(delay_per_click)
    
    print(f"[AÇÃO] Deploy de {num_total_goblin_clicks} cliques de goblins distribuídos pelas bordas concluído.")
    return True


def attack_cycle(tempo_ataque_segundos=60):
    print("\n--- Iniciando Novo Ciclo de Ataque ---")

    if not click_on_image(IMG_ATACAR_VILA, confidence=0.75): 
        print("[ERRO_CICLO] Botão 'Atacar!' na vila não encontrado. O bot está na tela correta?")
        return False
    time.sleep(4) 

    if not click_on_image(IMG_BUSCAR_AGORA, confidence=0.75): 
        print("[AVISO_CICLO] Botão 'Buscar Agora' não encontrado.")
    time.sleep(7) 

    # Chamada atualizada para deploy_troops com 90 goblins
    if not deploy_troops(num_total_goblin_clicks=90, points_per_edge=5, delay_per_click=0.05):
        print("[AVISO_CICLO] Problema no deploy das tropas.")
    
    print(f"[INFO_CICLO] Aguardando {tempo_ataque_segundos} segundos durante o ataque...")
    time.sleep(tempo_ataque_segundos)

    print("[AÇÃO_CICLO] Tentando encerrar a batalha...")
    if click_on_image(IMG_ENCERRAR_BATALHA, confidence=0.7):
        print("[INFO_CICLO] Botão 'Encerrar Batalha' clicado.")
        time.sleep(0.5)
        if os.path.exists(IMG_CONFIRMAR_ENCERRAR): 
            if click_on_image(IMG_CONFIRMAR_ENCERRAR, confidence=0.8):
                print("[INFO_CICLO] Encerramento de batalha confirmado.")
    else:
        print("[AVISO_CICLO] Botão 'Encerrar Batalha' não encontrado.")

    time.sleep(3)

    print("[AÇÃO_CICLO] Tentando retornar à base...")
    if not click_on_image(IMG_RETORNAR_BASE, confidence=0.8):
        print("[AVISO_CICLO] Botão 'Retornar à Base' não encontrado.")
    else:
        print("[INFO_CICLO] Retornado à base.")

    time.sleep(5)
    print("--- Ciclo de Ataque Concluído ---")
    return True

# --- Loop Principal do Bot ---
if __name__ == "__main__":
    ensure_debug_dir() 

    if not os.path.isdir(IMAGE_DIR):
        print(f"[ERRO FATAL] A pasta de imagens '{IMAGE_DIR}' não foi encontrada!")
        print("Crie esta pasta e coloque as imagens dos botões do jogo nela.")
        exit()
    
    imagens_essenciais = [IMG_ATACAR_VILA, IMG_BUSCAR_AGORA, IMG_SUPER_GOBLIN, IMG_ENCERRAR_BATALHA, IMG_RETORNAR_BASE]
    for img_path in imagens_essenciais:
        if not os.path.exists(img_path):
            print(f"[ERRO FATAL] Imagem essencial não encontrada: {img_path}")
            print("Por favor, crie esta imagem e coloque na pasta 'imagens'.")
            exit()
            
    initial_deploy_area = get_deployment_area_rect()
    if initial_deploy_area is None: 
        print(f"[ERRO FATAL] Não foi possível determinar a área de deploy.")
        exit()

    numero_total_de_ataques = 1 
    ataques_bem_sucedidos = 0

    print(">>> BOT DE CLASH OF CLANS INICIADO (COM MODO DEBUG ATIVO) <<<")
    print(f"ATENÇÃO: Certifique-se de que o LDPlayer com o Clash of Clans esteja visível e ativo.")
    print(f"Imagens de depuração serão salvas em '{DEBUG_IMAGE_DIR}'.")
    print(f"Você tem 5 segundos para preparar a janela.")
    time.sleep(5)

    try:
        for i in range(numero_total_de_ataques):
            print(f"\n===> EXECUTANDO ATAQUE {i+1} de {numero_total_de_ataques} <===")
            if attack_cycle(tempo_ataque_segundos=60):
                ataques_bem_sucedidos += 1
            else:
                print(f"[ERRO_MAIN] Falha no ciclo de ataque {i+1}.")
            
            if i < numero_total_de_ataques - 1:
                pausa_entre_ataques = 30 
                print(f"[INFO_MAIN] Aguardando {pausa_entre_ataques} segundos antes do próximo ataque...")
                time.sleep(pausa_entre_ataques)

    except KeyboardInterrupt:
        print("\n[INFO] Bot interrompido pelo usuário (Ctrl+C).")
    except Exception as e:
        print(f"[ERRO FATAL INESPERADO] {e}")
    finally:
        print(f"\n>>> BOT FINALIZADO <<<")
        print(f"Total de ataques programados: {numero_total_de_ataques}")
        print(f"Total de ciclos de ataque aparentemente bem-sucedidos: {ataques_bem_sucedidos}")
