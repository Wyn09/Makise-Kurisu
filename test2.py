from var_bridge_flow import SHARE_STATE
import multiprocessing

if __name__ == "__main__":
    # Windows必须的启动保护
    multiprocessing.freeze_support()  # 添加这一行
    
    print(SHARE_STATE.user_input)
    print("SHARE_STATE 类型：", type(SHARE_STATE))