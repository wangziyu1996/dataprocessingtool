import pandas as pd
import os

try:
    _current_dir = os.path.dirname(os.path.abspath(__file__))
    _csv_path = os.path.join(_current_dir, 'tester_kpi_mapping.csv')

    # 使用 pandas 读取CSV文件
    # 我们将这个DataFrame保存在一个名为 kpi_df 的变量中
    # 之后，其他模块可以通过 `from app.config.kpi_mapping import kpi_df` 来使用它
    kpi_df = pd.read_csv(_csv_path)
    
    if 'KPI' in kpi_df.columns:
        kpi_df['KPI'] = kpi_df['KPI'].str.replace(r'\\r|\\n', ' ', regex=True).str.strip()

except FileNotFoundError:
    # 异常处理：如果CSV文件不存在，就创建一个空的DataFrame，并打印错误信息
    # 这样可以避免程序因为找不到文件而崩溃
    print(f"错误：KPI映射文件未找到，路径：{_csv_path}")
    kpi_df = pd.DataFrame(columns=['Project', 'Tester', 'KPI', 'USL', 'LSL'])
except Exception as e:
    # 捕获其他可能的异常
    print(f"读取KPI映射文件时发生未知错误: {e}")
    kpi_df = pd.DataFrame(columns=['Project', 'Tester', 'KPI', 'USL', 'LSL'])

