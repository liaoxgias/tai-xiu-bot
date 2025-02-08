import numpy as np
from playwright.sync_api import sync_playwright
import cv2
from PIL import Image
import io
import json
import time

defaultBetValue = 10_000
ACC_TEXT = "trannam55"
PASS_TEXT = "TRANnam55"
SPRINT = 0
BET_REAL = True

currentBetValue = defaultBetValue
history = []

currentMoney = -1

currentTaiCount = 0
currentXiuCount = 0
currentRs = ""
currentTimeCount = 50
startTime = 0
tai_or_xiu_v = "tai"
updated_taixiu_status = False

DANG_NHAP = (771, 525)
ACC_LOCATION = (490, 277)
PASS_LOCATION = (490, 358)

LOGIN_LOCATION = (750, 460)
TURN_OFF_NOTIFICATION = (1025, 178)
IN_GAME = (848, 356)

TO_CROP = (700, 410, 725, 425)

TAI_LOCATION = (273, 376)
XIU_LOCATION = (656, 376)
CONFIRM_BET_LOCATION = (465, 600)

RESULRT_LOCATION = (643, 442, 650, 450)

TAI_COUNT_LOCATION = (165, 290, 372,346)
XIU_COUNT_LOCATION = (563, 293, 775,346)
TIME_COUNT_LOCATION = (400, 279, 531, 365)
is_start = True
game_count = 0

IS_UP_LOCATION = (448, 237, 485, 252)

ONE_K_LOCATION = (175, 530)
TEN_K_LOCATION = (255, 530)
FIFTY_K_LOCATION = (340, 530)

IMG_REF = cv2.imread("playing-game.png") 

def turn_off_notification(page):
    print("Turning off notification")
    for i in range(3):
        page.mouse.click(TURN_OFF_NOTIFICATION[0],TURN_OFF_NOTIFICATION[1])
        page.wait_for_timeout(500)
    print("Turned off notification")

def in_game(page):
    print("Game loading")
    page.mouse.click(IN_GAME[0],IN_GAME[1])
    page.wait_for_timeout(15_000)

def login(page):
    page.goto("https://play.bay789.top/")
    page.wait_for_selector("iframe")
    page.wait_for_timeout(500)  # Chờ 5 giây

    page.mouse.click(DANG_NHAP[0],DANG_NHAP[1])
    page.wait_for_timeout(500) 

    page.mouse.click(ACC_LOCATION[0],ACC_LOCATION[1])
    page.keyboard.type(ACC_TEXT)

    page.mouse.click(PASS_LOCATION[0],PASS_LOCATION[1])
    page.keyboard.type(PASS_TEXT)

    page.mouse.click(LOGIN_LOCATION[0],LOGIN_LOCATION[1])

    page.wait_for_timeout(2_000)  # Chờ 5 giây

    print("Logged in")

def game_load(page):
    login(page)
    turn_off_notification(page)
    in_game(page)

def calculate_similar(img, img_ref):
    diff = cv2.absdiff(img, img_ref)
    gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) 
    _, thresh = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
    num_diff_pixels = np.count_nonzero(thresh)
    total_pixels = 25 * 15  # Tổng số pixel trong ảnh cắt
    return 100 - (num_diff_pixels / total_pixels * 100)

def calculate_similar_v2(img, img_ref):
    diff = cv2.absdiff(img, img_ref)
    
    # Tính tổng sự khác biệt màu sắc theo khoảng cách Euclidean
    diff_norm = np.linalg.norm(diff, axis=2)
    
    # Ngưỡng để xác định pixel có sự khác biệt đáng kể
    threshold = 30  # Có thể điều chỉnh giá trị này
    num_diff_pixels = np.count_nonzero(diff_norm > threshold)
    
    # Tổng số pixel trong ảnh cắt
    total_pixels = img.shape[0] * img.shape[1] 
    
    # Tính toán phần trăm giống nhau
    similarity = 100 - (num_diff_pixels / total_pixels * 100)
    return similarity
def validate_structure(data):
    # Kiểm tra xem data có phải là list và có đúng 2 phần tử
    if not isinstance(data, list) or len(data) != 2:
        return False
    
    # Kiểm tra phần tử đầu tiên có phải là số nguyên không
    if not isinstance(data[0], int):
        return False
    
    # Kiểm tra phần tử thứ hai có phải là dictionary không
    if not isinstance(data[1], dict):
        return False
    
    expected_keys = {
        "uid": str,  # ID duy nhất
        "a": str,  # URL ảnh avatar
        "As": dict,  # Thông tin tài khoản
        "u": str,  # Tên người dùng
        "g": int,  # Giá trị nào đó (giả định là số nguyên)
        "ph": str,  # Số điện thoại
        "dn": str,  # Tên hiển thị
        "cmd": int,  # Mã lệnh
        "id": int,  # ID người dùng
        "pvr": bool  # Trạng thái (true/false)
    }
    
    if set(data[1].keys()) != set(expected_keys.keys()):
        return False
    
    for key, value_type in expected_keys.items():
        if not isinstance(data[1][key], value_type):
            return False
    
    # Kiểm tra cấu trúc của "As"
    expected_as_keys = {"gold": int, "chip": int, "guarranteed_chip": int, "guarranteed_gold": int, "safe": int, "vip": int}
    if set(data[1]["As"].keys()) != set(expected_as_keys.keys()):
        return False
    
    for key, value_type in expected_as_keys.items():
        if not isinstance(data[1]["As"][key], value_type):
            return False
    
    return True

def is_in_game(page):
    img = screenshot(page)
    img_ref = IMG_REF
    crop_img = img[TO_CROP[1]:TO_CROP[3], TO_CROP[0]:TO_CROP[2]]
    crop_img_ref = img_ref[TO_CROP[1]:TO_CROP[3], TO_CROP[0]:TO_CROP[2]]
    similarity = calculate_similar(crop_img, crop_img_ref)
    print("Similarity: ", similarity)
    return similarity > 90

def is_up():
    global startTime
    return startTime + 48 - round(time.time()) > 0 

def save_to_json(data, filename="data.json"):
    """Lưu danh sách đối tượng vào file JSON."""
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        # print(f"Data successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving data to JSON: {e}")


def bet_tai(page, value):
    global BET_REAL
    print("BET TAI")
    if not BET_REAL:
        return
    page.mouse.click(TAI_LOCATION[0],TAI_LOCATION[1])
    page.wait_for_timeout(300)
    click_value(value)
    confirm_bet(page)

def bet_xiu(page, value):
    global BET_REAL
    print("BET XIU")
    if not BET_REAL:
        return
    page.mouse.click(XIU_LOCATION[0],XIU_LOCATION[1])
    page.wait_for_timeout(100)
    click_value(value)
    confirm_bet(page)


ALL_IN_LOCATION = (270, 595)
def all_in(page, value):
    global BET_REAL
    print("ALL INN")
    if not BET_REAL:
        return
    if value == "tai":
        page.mouse.click(TAI_LOCATION[0],TAI_LOCATION[1])
    else :
        page.mouse.click(XIU_LOCATION[0],XIU_LOCATION[1])
    page.wait_for_timeout(200)
    page.mouse.click(ALL_IN_LOCATION[0],ALL_IN_LOCATION[1])
    page.wait_for_timeout(200)
    confirm_bet(page)

def filterData(data):
    global currentTaiCount, currentXiuCount, currentRs, startTime, currentTimeCount, updated_taixiu_status, game_count
    result = {
        "rs": data[1]["rS"],
        "tai": data[1]["gi"][0]["B"]["tB"],
        "xiu": data[1]["gi"][0]["S"]["tB"],
    }
    currentTaiCount = result["tai"]
    currentXiuCount = result["xiu"]
    if (currentRs != result["rs"]):
        startTime = round(time.time())
        currentRs = result["rs"]
        updated_taixiu_status = False
        game_count += 1
        
    currentTimeCount = startTime + 48 - round(time.time()) 

def screenshot(page):
    screenshot = page.screenshot()
    screenshot_np = np.array(Image.open(io.BytesIO(screenshot)))  # PIL mở ảnh từ bộ nhớ
    img = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
    return img

def click_value(value):
    while(value >= 50_000):
        page.mouse.click(FIFTY_K_LOCATION[0],FIFTY_K_LOCATION[1])
        value -= 50_000
        page.wait_for_timeout(200)
    while(value >= 10_000):
        page.mouse.click(TEN_K_LOCATION[0],TEN_K_LOCATION[1])
        value -= 10_000
        page.wait_for_timeout(200)
    while(value >= 1_000):
        page.mouse.click(ONE_K_LOCATION[0],ONE_K_LOCATION[1])
        value -= 1_000
        page.wait_for_timeout(200)

def confirm_bet(page):
    page.mouse.click(CONFIRM_BET_LOCATION[0],CONFIRM_BET_LOCATION[1])
    page.wait_for_timeout(200)

def tai_or_xiu(page):
    global updated_taixiu_status, tai_or_xiu_v
    if (updated_taixiu_status):
        return tai_or_xiu_v
    print("Checking tai or xiu")
    updated_taixiu_status = True
    img = screenshot(page)
    crop_img = img[RESULRT_LOCATION[1]:RESULRT_LOCATION[3], RESULRT_LOCATION[0]:RESULRT_LOCATION[2]]
    img_ref = IMG_REF
    crop_img_ref = img_ref[RESULRT_LOCATION[1]:RESULRT_LOCATION[3], RESULRT_LOCATION[0]:RESULRT_LOCATION[2]]
    similarity = calculate_similar_v2(crop_img, crop_img_ref)
    # save image
    if (similarity > 50):
        tai_or_xiu_v = "xiu"
        return "xiu"
    else:
        tai_or_xiu_v = "tai"
        return "tai"

def safe_parse_int(value):
    try:
        if (str(value) == "G"):
            return 6
        return int(str(value).replace(",",""))
    except ValueError:
        print(f"Error: Cannot convert '{value}' to an integer.")
        return None  # Hoặc có thể trả về một giá trị mặc định

def choosing(page, tai_count, xiu_count, time_count, betValue, is_all_in = False):
    global game_count
    time_count = safe_parse_int(time_count)
    if (time_count == None or time_count > 5 or time_count < 3 or game_count < 2):
        print("Chưa đến lúc đặt, kiên nhẫn")
        return (False,0)
    beted = ""
    if (abs(tai_count-xiu_count) < SPRINT):
        return (False,1)
    
    if is_all_in:
        if (tai_count < xiu_count):
            all_in(page, "tai")
            return (True, "tai")
        else:
            all_in(page, "xiu")
            return (True, "xiu")
    if tai_count > xiu_count:
        bet_xiu(page, betValue)
        beted = "xiu"
    else:
        bet_tai(page, betValue)
        beted = "tai"
    page.wait_for_timeout(1_000)
    return (True, beted)

def printSth(tai_count, xiu_count, time_count, prefResult):
    global game_count
    print("\t------------------------------------------")
    print("\t|\tGame count: ", game_count)
    print("\t|\tTai count: ", tai_count)
    print("\t|\tXiu count: ", xiu_count)
    print("\t|\tTime count: ", time_count)
    print("\t|\tPrevious Result: ", prefResult)
    print("\t|\tCurrent money: ", currentMoney)
    print("\t------------------------------------------")

def handleEvent(event):
    global currentMoney
    try:
        data = json.loads(event)

        # Nếu dữ liệu đúng format, in ra
        if currentMoney == -1:
            try :
                if validate_structure(data):
                    currentMoney = data[1]["As"]["gold"]
                    print("Data: ", data)
                    print("Current money: ", currentMoney)
            except:
                a = 1

        if is_valid_event(data):
            filterData(data)

    except:
        return

def on_websocket(ws):
    print(f"WebSocket opened: {ws.url}") 

    # Lắng nghe tin nhắn nhận được từ WebSocket
    ws.on("framereceived", lambda frame: handleEvent(frame))

    ws.on("close", lambda: print(f"[WebSocket Closed] {ws.url}"))

prefTaiCount = 0
prefXiuCount = 0
tai_count = 0
xiu_count = 0

prefDoor = "deldat"

is_beted = False
is_new_round = False

expected_keys = {
    "rS": str,  # Chuỗi hash
    "gi": list,  # Danh sách chứa object {"B": {...}, "S": {...}, "aid": ...}
    "j": int,  # Một số nguyên
    "cmd": int,  # Một số nguyên (mã lệnh)
    "sid": int  # Một số nguyên (ID phiên)
}

def is_valid_event(data):
    """
    Kiểm tra nếu data có cùng format với mẫu.
    """
    global startTime
    if (data[0] != 5):
        return False
    if not isinstance(data, list) or len(data) != 2 or not isinstance(data[1], dict):
        return False  # Phải là list và có ít nhất 2 phần tử, phần tử thứ 2 phải là dict

    second_dict = data[1]  # Phần tử dictionary thứ hai
    if len(second_dict["rS"]) < 5:
        return False
    
    if game_count >= 2 and startTime + 60 - round(time.time()) > 0 and currentRs != second_dict["rS"]:
        return False
        
    if set(data[1].keys()) != set(expected_keys.keys()):
        return False  # Phải có đủ các key như mẫu

    for key, expected_type in expected_keys.items():
        if key not in second_dict or not isinstance(second_dict[key], expected_type):
            return False  # Nếu thiếu key hoặc sai kiểu dữ liệu, loại bỏ

    # Kiểm tra format của `gi` (phải là danh sách các object có "B", "S", "aid")
    if isinstance(second_dict["gi"], list):
        for item in second_dict["gi"]:
            if not isinstance(item, dict) or "B" not in item or "S" not in item or "aid" not in item:
                return False  # "gi" phải là danh sách chứa object có "B", "S", "aid"
            
    if len(second_dict["gi"]) != 2: 
        return False

    print(data[1])
    return True  # Nếu tất cả điều kiện đều đúng, dữ liệu hợp lệ

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # headless=False để hiển thị trình duyệt
    page = browser.new_page()
    page.on("websocket", on_websocket)
    
    game_load(page)

    # ensure in game
    limit = 10
    while(not is_in_game(page) and limit > 0):
        limit -= 1
        print("Limit: ", limit)
        page.wait_for_timeout(2_000)
    x = 0
    lose_row = 0

    while(True):
        print("-----------------------------------------------");
        isup = is_up()
        if (not isup):
            x +=1
            is_new_round = True
            temp = currentTaiCount
            if (temp != None and x < 3):
                prefTaiCount = temp
            temp = currentXiuCount
            if (temp != None and x < 3):
                prefXiuCount = temp
            print(f"Tai Count: {prefTaiCount}")
            print(f"Xiu Count: {prefXiuCount}")
            is_beted = False
        else:
            ## Load data from screen
            x = 0
            tai_count = currentTaiCount
            xiu_count = currentXiuCount
            time_count = startTime + 48 - round(time.time())
            prefResult = tai_or_xiu(page)
            if (currentMoney > 200_000):
                print("Biết điểm dừng rồi, nghỉ chơi")
                exit(1)
            
            ## Set value before bet, save history
            if is_new_round and is_start:
                print(f"Kết quả game trước: {prefResult}, cược vào {prefDoor}")
                if prefDoor == "deldat":
                    history.append({"game_count": game_count-1, "tai": prefTaiCount, "xiu": prefXiuCount, "door": prefDoor, "bet": currentBetValue, "isWin": None, "money": currentMoney})
                    currentBetValue = currentBetValue

                elif prefResult != prefDoor:
                    lose_row += 1
                    history.append({"game_count": game_count-1, "tai": prefTaiCount, "xiu": prefXiuCount, "door": prefDoor, "bet": currentBetValue, "isWin": False, "money": currentMoney})
                    if lose_row >= 2:
                        currentBetValue *= 2
                else:
                    lose_row = 0
                    currentMoney += currentBetValue * (198/100)
                    history.append({"game_count": game_count-1, "tai": prefTaiCount, "xiu": prefXiuCount, "door": prefDoor, "bet": currentBetValue, "isWin": True, "money": currentMoney})
                    currentBetValue = defaultBetValue
                
                save_to_json(history, "history.json")

                print(f"Set current bet value to: {currentBetValue}")
                is_new_round = False
                
            ## Wait to bet.
            if is_start and not is_beted:
                if (currentMoney == 0):
                    print("DJTME hết tiền rồi")
                    exit(1)
                isAllIn = currentMoney < currentBetValue
                isBeted, value = choosing(page, tai_count, xiu_count, time_count, currentBetValue,isAllIn)
                if (isBeted):
                    is_beted = True
                    prefDoor = value
                    if isAllIn:
                        currentBetValue = currentMoney
                        currentMoney = 0
                    else:
                        currentMoney -= currentBetValue
                    print(f"Bet success on {value} with ${currentBetValue}")
                elif value == 1:
                    print("Lệch chưa đủ sâu để đặt")
                    prefDoor = "deldat"

            if is_beted:
                print(f"Đã bet vào {prefDoor}, ngồi chờ")
            else:
                prefDoor = "deldat"
            
            printSth(tai_count, xiu_count, time_count, prefResult)

            # Nếu game này vào cửa trên thì bắt đầu đặt
            # if is_start == False:
            #     if prefTaiCount > prefXiuCount and tai_or_xiu(page) == "tai":
            #         print("Oke, vào cửa trên, bắt đầu đặt")
            #         is_start = True
            #     elif prefTaiCount < prefXiuCount and tai_or_xiu(page) == "xiu":
            #         print("Oke, vào cửa trên, bắt đầu đặt")
            #         is_start = True
            #     else:
            #        print("Vô cửa dưới, chưa đặt")
        
            
        page.wait_for_timeout(1_000)
    page.wait_for_timeout(10000_000)  # Chờ 100 giây


    ##949870bdd23bc53193da17a388755104