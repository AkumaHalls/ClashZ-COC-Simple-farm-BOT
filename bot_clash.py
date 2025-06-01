import pyautogui
import cv2
import numpy as np
import time
import os
from PIL import ImageGrab, Image
import keyboard # Importa a biblioteca keyboard

# --- Configurações Iniciais ---
IMAGE_DIR = "imagens"
DEBUG_IMAGE_DIR = "imagens_debug"
DEBUG_MODE = True

# Nomes dos arquivos de imagem
IMG_ATACAR_VILA = os.path.join(IMAGE_DIR, "atacar_vila.png")
IMG_BUSCAR_AGORA = os.path.join(IMAGE_DIR, "buscar_agora.png")
IMG_SUPER_GOBLIN = os.path.join(IMAGE_DIR, "super_goblin.png")
IMG_ENCERRAR_BATALHA = os.path.join(IMAGE_DIR, "encerrar_batalha.png")
IMG_CONFIRMAR_ENCERRAR = os.path.join(IMAGE_DIR, "confirmar_encerrar.png")
IMG_RETORNAR_BASE = os.path.join(IMAGE_DIR, "retornar_base.png")

DEPLOYMENT_AREA_RECT = None
AUTO_DEPLOY_MARGIN_X_PERCENT = 0.18
AUTO_DEPLOY_MARGIN_Y_PERCENT = 0.22

# --- Variável Global para Parada de Emergência ---
parada_emergencia_ativada = False

# --- Função para Parada de Emergência ---
def ativar_parada_emergencia(e):
    """Função chamada quando a tecla de emergência é pressionada."""
    global parada_emergencia_ativada
    if e.name == 'insert': # Verifica se a tecla pressionada é 'insert'
        if not parada_emergencia_ativada: # Evita múltiplas mensagens se a tecla for mantida pressionada
            print("\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("!!! PARADA DE EMERGÊNCIA (INSERT) ATIVADA !!!")
            print("!!! O BOT IRÁ PARAR EM BREVE.           !!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n")
        parada_emergencia_ativada = True

# Registra a função para a tecla 'insert'
# O try-except é para lidar com casos onde o registro do hook pode falhar (ex: permissões)
try:
    keyboard.on_press(ativar_parada_emergencia)
    print("[INFO] Tecla de emergência 'Insert' registrada. Pressione 'Insert' a qualquer momento para parar o bot.")
except Exception as e_keyboard:
    print(f"[AVISO] Não foi possível registrar a tecla de emergência 'Insert': {e_keyboard}")
    print("[AVISO] A parada por 'Insert' pode não funcionar. Use Ctrl+C no terminal como alternativa.")


# --- Funções Auxiliares ---

def ensure_debug_dir():
    if DEBUG_MODE and not os.path.exists(DEBUG_IMAGE_DIR):
        os.makedirs(DEBUG_IMAGE_DIR)

def find_image_on_screen(template_image_path, confidence=0.8, region=None):
    global parada_emergencia_ativada
    if parada_emergencia_ativada: return None # Verifica antes de processar

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
                try:
                    screen_pil.save(os.path.join(DEBUG_IMAGE_DIR, f"debug_screenshot_region_{base_template_name}"))
                except Exception as e_save_region:
                    print(f"[AVISO_DEBUG] Não foi possível salvar screenshot da região: {e_save_region}")
        else:
            screen_pil = ImageGrab.grab()

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
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= confidence:
            pt = max_loc
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            if region:
                center_x += region[0]
                center_y += region[1]
            print(f"[INFO] Imagem '{base_template_name}' encontrada em: ({center_x}, {center_y}) com confiança: {max_val:.2f} (requerido: {confidence:.2f})")
            return (center_x, center_y)
        else:
            if DEBUG_MODE and not parada_emergencia_ativada: # Não poluir o log se a parada já foi ativada
                print(f"[DEBUG] Imagem '{base_template_name}' NÃO encontrada. Confiança máxima: {max_val:.2f} (requerido: {confidence:.2f}). Salvando screenshot para análise.")
                debug_screenshot_path = os.path.join(DEBUG_IMAGE_DIR, f"debug_screenshot_FAIL_{base_template_name}")
                screen_pil.save(debug_screenshot_path)
                print(f"[DEBUG] Screenshot salvo em: {debug_screenshot_path}")
            return None
    except Exception as e:
        if not parada_emergencia_ativada:
            print(f"[ERRO] em find_image_on_screen para '{template_image_path}': {e}")
        return None

def click_on_image(image_path, confidence=0.8, duration=0.1, region=None, clicks=1, interval=0.1):
    global parada_emergencia_ativada
    if parada_emergencia_ativada: return False

    coords = find_image_on_screen(image_path, confidence, region)
    if coords:
        if parada_emergencia_ativada: return False # Checagem dupla
        pyautogui.moveTo(coords[0], coords[1], duration=duration)
        if parada_emergencia_ativada: return False
        pyautogui.click(clicks=clicks, interval=interval)
        print(f"[INFO] Clicado em '{os.path.basename(image_path)}' em {coords}")
        return True
    return False

def wait_for_image(image_path, timeout_seconds=10, confidence=0.8, region=None):
    global parada_emergencia_ativada
    print(f"[INFO] Esperando pela imagem '{os.path.basename(image_path)}' por até {timeout_seconds}s...")
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if parada_emergencia_ativada: return None
        coords = find_image_on_screen(image_path, confidence, region)
        if coords:
            print(f"[INFO] Imagem '{os.path.basename(image_path)}' apareceu.")
            return coords
        time.sleep(0.2) # Reduzido para checar parada de emergência mais rápido
    if not parada_emergencia_ativada:
        print(f"[AVISO] Tempo esgotado esperando por '{os.path.basename(image_path)}'.")
    return None

# --- Lógica do Jogo ---

def get_deployment_area_rect():
    global DEPLOYMENT_AREA_RECT
    if DEPLOYMENT_AREA_RECT is not None and isinstance(DEPLOYMENT_AREA_RECT, tuple) and len(DEPLOYMENT_AREA_RECT) == 4:
        # print(f"[INFO_DEPLOY] Usando área de deploy manual: {DEPLOYMENT_AREA_RECT}") # Removido para reduzir logs
        return DEPLOYMENT_AREA_RECT

    print("[INFO_DEPLOY] DEPLOYMENT_AREA_RECT não definido manualmente. Calculando área de deploy automática...")
    screen_width, screen_height = pyautogui.size()
    margin_x = int(screen_width * AUTO_DEPLOY_MARGIN_X_PERCENT)
    margin_y = int(screen_height * AUTO_DEPLOY_MARGIN_Y_PERCENT)
    auto_left = margin_x
    auto_top = margin_y
    auto_width = screen_width - (2 * margin_x)
    auto_height = screen_height - (2 * margin_y)
    DEPLOYMENT_AREA_RECT = (auto_left, auto_top, auto_width, auto_height)
    print(f"[INFO_DEPLOY] Área de deploy automática calculada: {DEPLOYMENT_AREA_RECT}")
    return DEPLOYMENT_AREA_RECT


def deploy_troops(num_total_goblin_clicks=90, points_per_edge=5, delay_per_click=0.1):
    global parada_emergencia_ativada
    print("[AÇÃO] Iniciando deploy de tropas pelas bordas (modo simétrico)...")
    
    current_deployment_area = get_deployment_area_rect()
    if current_deployment_area is None:
        print("[ERRO_DEPLOY] Não foi possível obter a área de deploy.")
        return False
    if parada_emergencia_ativada: return False

    if not click_on_image(IMG_SUPER_GOBLIN, confidence=0.4):
        if not parada_emergencia_ativada: # Só imprime erro se não for parada de emergência
            print("[ERRO_DEPLOY] Não foi possível selecionar Super Goblin. Abortando deploy.")
        return False
    if parada_emergencia_ativada: return False
    
    time.sleep(0.3) 

    left, top, width, height = current_deployment_area
    right = left + width
    bottom = top + height
    actual_points_per_edge = max(1, points_per_edge) 

    top_coords, right_coords, bottom_coords, left_coords = [], [], [], []

    # Gerar pontos (código omitido para brevidade, igual ao anterior)
    if actual_points_per_edge == 1:
        top_coords.append({'x': left + width // 2, 'y': top, 'edge': 'top'})
    else:
        step_x = width / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            top_coords.append({'x': left + int(step_x * i), 'y': top, 'edge': 'top'})
    if actual_points_per_edge == 1:
        right_coords.append({'x': right, 'y': top + height // 2, 'edge': 'right'})
    else:
        step_y = height / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            right_coords.append({'x': right, 'y': top + int(step_y * i), 'edge': 'right'})
    if actual_points_per_edge == 1:
        bottom_coords.append({'x': left + width // 2, 'y': bottom, 'edge': 'bottom'})
    else:
        step_x = width / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            bottom_coords.append({'x': right - int(step_x * i), 'y': bottom, 'edge': 'bottom'})
    if actual_points_per_edge == 1:
        left_coords.append({'x': left, 'y': top + height // 2, 'edge': 'left'})
    else:
        step_y = height / (actual_points_per_edge - 1)
        for i in range(actual_points_per_edge):
            left_coords.append({'x': left, 'y': bottom - int(step_y * i), 'edge': 'left'})

    all_deploy_coords_intercalated = []
    max_len = actual_points_per_edge
    for i in range(max_len):
        if i < len(top_coords): all_deploy_coords_intercalated.append(top_coords[i])
        if i < len(right_coords): all_deploy_coords_intercalated.append(right_coords[i])
        if i < len(bottom_coords): all_deploy_coords_intercalated.append(bottom_coords[i])
        if i < len(left_coords): all_deploy_coords_intercalated.append(left_coords[i])
    
    if not all_deploy_coords_intercalated:
        print("[AVISO_DEPLOY] Nenhum ponto de deploy foi gerado.")
        return False

    print(f"[INFO_DEPLOY] Gerados {len(all_deploy_coords_intercalated)} pontos de deploy distintos.")
    
    for i in range(num_total_goblin_clicks):
        if parada_emergencia_ativada:
            print("[INFO_DEPLOY] Parada de emergência durante o deploy de tropas.")
            return False # Interrompe o deploy
        
        coord_data = all_deploy_coords_intercalated[i % len(all_deploy_coords_intercalated)]
        pyautogui.moveTo(coord_data['x'], coord_data['y'], duration=0.02) 
        pyautogui.click()
        time.sleep(delay_per_click) 
    
    print(f"[AÇÃO] Deploy de {num_total_goblin_clicks} cliques de goblins concluído.")
    return True


def attack_cycle(tempo_ataque_segundos=60):
    global parada_emergencia_ativada
    print("\n--- Iniciando Novo Ciclo de Ataque ---")

    if parada_emergencia_ativada: return False
    if not click_on_image(IMG_ATACAR_VILA, confidence=0.75): 
        if not parada_emergencia_ativada: print("[ERRO_CICLO] Botão 'Atacar!' na vila não encontrado.")
        return False
    
    if parada_emergencia_ativada: return False
    time.sleep(4) 

    if parada_emergencia_ativada: return False
    if not click_on_image(IMG_BUSCAR_AGORA, confidence=0.75): 
        if not parada_emergencia_ativada: print("[AVISO_CICLO] Botão 'Buscar Agora' não encontrado.")
    
    if parada_emergencia_ativada: return False
    time.sleep(7) 

    if parada_emergencia_ativada: return False
    if not deploy_troops(num_total_goblin_clicks=90, points_per_edge=5):
        if not parada_emergencia_ativada: print("[AVISO_CICLO] Problema no deploy das tropas.")
        # Mesmo se o deploy falhar (ou for interrompido), continua para tentar encerrar
    
    if parada_emergencia_ativada:
        print("[INFO_CICLO] Parada de emergência antes de aguardar o tempo de ataque.")
        # Tenta encerrar a batalha mesmo assim
        if click_on_image(IMG_ENCERRAR_BATALHA, confidence=0.7):
            time.sleep(0.5)
            if os.path.exists(IMG_CONFIRMAR_ENCERRAR):
                click_on_image(IMG_CONFIRMAR_ENCERRAR, confidence=0.8)
        return False # Indica que o ciclo foi interrompido

    print(f"[INFO_CICLO] Aguardando {tempo_ataque_segundos} segundos durante o ataque...")
    # Loop de espera que verifica a parada de emergência
    tempo_inicial_espera = time.time()
    while time.time() - tempo_inicial_espera < tempo_ataque_segundos:
        if parada_emergencia_ativada:
            print("[INFO_CICLO] Parada de emergência durante o tempo de ataque.")
            break # Sai do loop de espera
        time.sleep(0.2) # Verifica a cada 0.2 segundos

    if parada_emergencia_ativada: # Se saiu do loop por parada de emergência
        if click_on_image(IMG_ENCERRAR_BATALHA, confidence=0.7):
            time.sleep(0.5)
            if os.path.exists(IMG_CONFIRMAR_ENCERRAR):
                click_on_image(IMG_CONFIRMAR_ENCERRAR, confidence=0.8)
        return False


    print("[AÇÃO_CICLO] Tentando encerrar a batalha...")
    if click_on_image(IMG_ENCERRAR_BATALHA, confidence=0.7):
        print("[INFO_CICLO] Botão 'Encerrar Batalha' clicado.")
        time.sleep(0.5)
        if os.path.exists(IMG_CONFIRMAR_ENCERRAR): 
            click_on_image(IMG_CONFIRMAR_ENCERRAR, confidence=0.8)
    else:
        if not parada_emergencia_ativada: print("[AVISO_CICLO] Botão 'Encerrar Batalha' não encontrado.")

    if parada_emergencia_ativada: return False # Verifica antes de longas pausas
    time.sleep(3)

    if parada_emergencia_ativada: return False
    print("[AÇÃO_CICLO] Tentando retornar à base...")
    if not click_on_image(IMG_RETORNAR_BASE, confidence=0.8):
        if not parada_emergencia_ativada: print("[AVISO_CICLO] Botão 'Retornar à Base' não encontrado.")
    else:
        print("[INFO_CICLO] Retornado à base.")

    if parada_emergencia_ativada: return False
    time.sleep(5)
    print("--- Ciclo de Ataque Concluído ---")
    return True

# --- Loop Principal do Bot ---
if __name__ == "__main__":
    ensure_debug_dir() 

    if not os.path.isdir(IMAGE_DIR):
        print(f"[ERRO FATAL] A pasta de imagens '{IMAGE_DIR}' não foi encontrada!")
        exit()
    
    imagens_essenciais = [IMG_ATACAR_VILA, IMG_BUSCAR_AGORA, IMG_SUPER_GOBLIN, IMG_ENCERRAR_BATALHA, IMG_RETORNAR_BASE]
    for img_path in imagens_essenciais:
        if not os.path.exists(img_path):
            print(f"[ERRO FATAL] Imagem essencial não encontrada: {img_path}")
            exit()
            
    initial_deploy_area = get_deployment_area_rect()
    if initial_deploy_area is None: 
        print(f"[ERRO FATAL] Não foi possível determinar a área de deploy.")
        exit()

    numero_total_de_ataques = 1 
    ataques_bem_sucedidos = 0

    print(">>> BOT DE CLASH OF CLANS INICIADO (COM MODO DEBUG ATIVO) <<<")
    print(f"ATENÇÃO: Certifique-se de que o LDPlayer com o Clash of Clans esteja visível e ativo.")
    print(f"Você tem 5 segundos para preparar a janela.")
    time.sleep(5)

    try:
        for i in range(numero_total_de_ataques):
            if parada_emergencia_ativada:
                print("[INFO_MAIN] Parada de emergência detectada antes de iniciar novo ciclo.")
                break
            print(f"\n===> EXECUTANDO ATAQUE {i+1} de {numero_total_de_ataques} <===")
            if attack_cycle(tempo_ataque_segundos=60):
                if not parada_emergencia_ativada: # Só conta como sucesso se não foi interrompido
                    ataques_bem_sucedidos += 1
            else:
                if parada_emergencia_ativada:
                    print(f"[INFO_MAIN] Ciclo de ataque {i+1} interrompido por parada de emergência.")
                else:
                    print(f"[ERRO_MAIN] Falha no ciclo de ataque {i+1}.")
            
            if parada_emergencia_ativada: break # Sai do loop principal de ataques

            if i < numero_total_de_ataques - 1:
                pausa_entre_ataques = 30 
                print(f"[INFO_MAIN] Aguardando {pausa_entre_ataques} segundos antes do próximo ataque...")
                # Loop de pausa que verifica a parada de emergência
                tempo_inicial_pausa = time.time()
                while time.time() - tempo_inicial_pausa < pausa_entre_ataques:
                    if parada_emergencia_ativada:
                        print("[INFO_MAIN] Parada de emergência durante a pausa entre ataques.")
                        break
                    time.sleep(0.2)
                if parada_emergencia_ativada: break 


    except KeyboardInterrupt: # Ctrl+C também funciona como parada
        print("\n[INFO] Bot interrompido pelo usuário (Ctrl+C).")
        parada_emergencia_ativada = True # Garante que a flag seja setada para a mensagem final
    except Exception as e:
        print(f"[ERRO FATAL INESPERADO] {e}")
    finally:
        if parada_emergencia_ativada:
            print("\n--- EXECUÇÃO INTERROMPIDA PELA TECLA DE EMERGÊNCIA 'INSERT' ---")
        print(f"\n>>> BOT FINALIZADO <<<")
        print(f"Total de ataques programados: {numero_total_de_ataques}")
        print(f"Total de ciclos de ataque concluídos (sem interrupção): {ataques_bem_sucedidos}")
        
        # É uma boa prática remover o hook do teclado ao final, embora o script vá terminar.
        # No entanto, keyboard.unhook_all() pode às vezes causar problemas se chamado muito abruptamente.
        # Para um script simples que termina, deixar o hook ativo até o fim do processo é geralmente ok.
        # Se você fosse rodar isso como um módulo ou em um loop mais longo, seria mais crítico.
        # Exemplo:
        # try:
        #     keyboard.unhook_all()
        #     print("[INFO] Hooks do teclado removidos.")
        # except Exception as e_unhook:
        #     print(f"[AVISO] Erro ao remover hooks do teclado: {e_unhook}")
