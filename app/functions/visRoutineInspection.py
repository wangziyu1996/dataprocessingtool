import pandas as pd
import numpy as np
import os
from collections import defaultdict
import json

from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.globals import CurrentConfig
from jinja2 import Environment, FileSystemLoader

from config.kpi_mapping import kpi_df

class VisRoutineInspection:
    def __init__(self, inputFilePath, outputFilePath):
        self.inputFilePath = inputFilePath
        self.outputFilePath = outputFilePath
        self.df = None

    def datacleansing(self):
        # --- 数据清洗流程 ---
        # 该流程将应用于 "All testers(expect OC&PST)",""All testers(expect OC)"","Weekly", "Daily", "OC-L1", "OC-L2" 等 sheet。

        sheet_names_to_process = ["All testers(expect OC&PST)","All testers(expect OC)","Weekly", "Daily", "OC-L1", "OC-L2"]
        processed_dfs = {}

        # 步骤 A: 循环处理所有目标 sheet
        for sheet_name in sheet_names_to_process:
            try:
                df = pd.read_excel(self.inputFilePath, sheet_name=sheet_name, header=None, dtype=object)
            except ValueError:
                print(f"Info: Sheet '{sheet_name}' not found in the input file. Skipping.")
                continue

            # --- [NEW] 根据 sheet 名称路由到不同的清洗方法 ---
            if sheet_name in ["OC-L1", "OC-L2"]:
                # 对 OC sheet 执行特殊的清洗流程
                df = self._clean_oc_df(df)
                if df.empty:
                    print(f"Warning: Cleaning failed for sheet '{sheet_name}', it will be skipped.")
                    continue
            else:
                # --- 开始处理常规 Sheet: {sheet_name} ---

                # 步骤 2: 预处理原始表头和数据
                df.iloc[0] = df.iloc[0].ffill()
                df = df.drop(df.index[3:11])

                # 步骤 3: 构建新的复合列标题
                row1 = df.iloc[0].fillna('').astype(str)
                row2 = df.iloc[1].fillna('').astype(str)
                row_original_3 = df.iloc[2].fillna('').astype(str)

                new_row_values = row1 + " " + row2 + " " + row_original_3

                # 使用 .T (转置) 的方法更健壮
                new_row_df = pd.DataFrame(new_row_values).T
                
                top_df = df.iloc[:2]
                bottom_df = df.iloc[2:]
                df = pd.concat([top_df, new_row_df, bottom_df]).reset_index(drop=True)

                # 步骤 4: 清理并设置最终的 DataFrame 结构
                df = df.drop([0, 1, 3]).reset_index(drop=True)
                
                # --- 防御性地设置表头，强制长度匹配 ---
                df_body = df.iloc[1:].copy()
                num_cols = df_body.shape[1]
                
                header_row = df.iloc[0].astype(str).str.strip()
                
                # --- [FIX] 标准化 'Date' 和 'Spec' 列名 (不区分大小写) ---
                header_row = header_row.replace(r'(?i)\bdate\b.*', 'Date', regex=True)
                header_row = header_row.replace(r'(?i)\bspec\b.*', 'Spec', regex=True)
                
                new_header = list(header_row)
                
                # 强制新表头的长度与数据体的列数一致
                if len(new_header) > num_cols:
                    final_header = new_header[:num_cols]
                else:
                    final_header = new_header + ['Unnamed: {}'.format(i) for i in range(num_cols - len(new_header))]

                # --- [FIX] 自动去重列名，防止后续操作因重名列而出错 ---
                seen = {}
                deduplicated_header = []
                for i, col in enumerate(final_header):
                    # --- [NEW] 标准化列名，去除重复的 "Unnamed" 和多余的空格 ---
                    clean_col = ' '.join(col.split()).replace('Unnamed: ', 'Unnamed_')
                    if clean_col in seen:
                        seen[clean_col] += 1
                        deduplicated_header.append(f"{clean_col}_{seen[clean_col]}")
                    else:
                        seen[clean_col] = 0
                        deduplicated_header.append(clean_col)
                
                df_body.columns = deduplicated_header
                df = df_body.reset_index(drop=True)
                # --- 表头设置结束 ---

                # 步骤 5: 格式化和清洗数据内容
                # (The rest of the function remains the same)
                
                # --- [FIX] 确保 'Date' 列存在后再进行处理 ---
                if 'Date' in df.columns:
                    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                    df.dropna(subset=['Date'], inplace=True)
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                else:
                    print(f"Warning: 'Date' column not found in sheet '{sheet_name}' after header processing. Skipping date operations.")

                try:
                    spec_col_index = df.columns.get_loc('Spec')
                    cols_to_check = df.columns[spec_col_index + 1:]
                    
                    df[cols_to_check] = df[cols_to_check].replace(['', None], np.nan)
                    df.dropna(subset=cols_to_check, how='all', inplace=True)

                    cols_to_drop = [
                        col for col in cols_to_check if col in df.columns and df[col].isnull().all()
                    ]
                    if cols_to_drop:
                        df.drop(columns=cols_to_drop, inplace=True)

                    # --- [NEW] 将 'Spec' 后的列中所有非数字字符串值转换为空值 (NaN) ---
                    for col in cols_to_check:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                except KeyError:
                    print(f"Warning: 'Spec' column not found in sheet '{sheet_name}'. Skipping row/column deletion.")

            # 将处理好的 DataFrame 存入字典
            processed_dfs[sheet_name] = df

        # 步骤 B: 检查是否有任何 sheet 被成功处理
        if not processed_dfs:
            raise ValueError("None of the target sheets were found or processed successfully in the input file.")

        # 将包含所有已处理 DataFrame 的字典赋值给 self.df
        self.df = processed_dfs

        # --- [NEW] 临时步骤: 将清洗后的数据写入 Excel 文件以供验证 ---

        # --- [NEW] 查找所有处理过的 sheet 中的最小和最大日期 ---
        min_date, max_date = None, None
        for df in self.df.values():
            if 'Date' in df.columns and not df['Date'].empty:
                current_min = pd.to_datetime(df['Date']).min()
                current_max = pd.to_datetime(df['Date']).max()
                if pd.notna(current_min):
                    if min_date is None or current_min < min_date:
                        min_date = current_min
                if pd.notna(current_max):
                    if max_date is None or current_max > max_date:
                        max_date = current_max
        
        return min_date, max_date

    def _clean_oc_df(self, df):
        """
        Performs a specific, multi-step cleaning process for 'OC-L1' and 'OC-L2' sheets.
        """
        try:
            # 1. 删除表格的1-16行
            df = df.drop(df.index[0:16]).reset_index(drop=True)

            # 2. 删除B-Z, AG-AM, AQ列
            # 获取列索引
            cols_to_drop = []
            
            # B-Z (index 1 to 25)
            for i in range(1, 26):
                if i < len(df.columns):
                    cols_to_drop.append(df.columns[i])
                    
            # AG-AM (index 32 to 38) 
            for i in range(32, 39):
                if i < len(df.columns):
                    cols_to_drop.append(df.columns[i])
                    
            # AQ (index 42)
            if 42 < len(df.columns):
                cols_to_drop.append(df.columns[42])
                
            df = df.drop(columns=cols_to_drop)
            
            # 3. 将保留下来的数据存入dataframe
            # 4. 设置新的表头
            new_headers = [
                'Date',
                'S1 Decenter(μm)-x',
                'S1 Decenter(μm)-y',
                'S1 Decenter(μm)-abs',
                'S2 Decenter(μm)-x',
                'S2 Decenter(μm)-y',
                'S2 Decenter(μm)-abs',
                'Tilt(\')-x',
                'Tilt(\')-y',
                'Tilt(\')-abs'
            ]
            
            # 确保列数与新表头数量一致
            if len(df.columns) != len(new_headers):
                if len(df.columns) > len(new_headers):
                    # 如果列数过多，截取前面的列
                    df = df.iloc[:, :len(new_headers)]
                else:
                    # 如果列数不足，添加空列
                    for i in range(len(df.columns), len(new_headers)):
                        df[f'Unnamed_{i}'] = np.nan
            
            df.columns = new_headers

            # 最终数据类型转换
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.dropna(subset=['Date'], inplace=True)
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

            # 将其他列转换为数值型
            for col in df.columns:
                if col != 'Date':
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            return df
        except Exception as e:
            # 保留异常处理但简化错误信息
            raise e
    
    def visualization(self, start_date, end_date, output_html_path):
        """
        根据日期范围筛选数据，并使用自定义 Jinja2 模板生成一个包含所有图表的 HTML 报告.
        """
        # --- 步骤 1: 初始化数据容器 ---
        tester_kpi_chart_options = defaultdict(dict)
        all_kpis_set = set()

        # --- 步骤 2 & 3: 循环处理数据并创建图表 ---
        for sheet_name, df in self.df.items():
            if df.empty or 'Date' not in df.columns:
                continue

            # --- 步骤 4: 日期筛选 ---
            temp_df = df.copy()
            temp_df['Date'] = pd.to_datetime(temp_df['Date'])
            mask = (temp_df['Date'] >= start_date) & (temp_df['Date'] <= end_date)
            filtered_df = temp_df[mask].sort_values(by='Date')

            if filtered_df.empty:
                continue

            # --- 特殊处理 OC-L1 和 OC-L2 ---
            if sheet_name in ['OC-L1', 'OC-L2']:
                # 定义需要生成的图表配置
                oc_configs = [
                    {'kpi': 'OCL1S1', 'title_suffix': 'S1 Decenter(μm)', 'columns': ['S1 Decenter(μm)-x', 'S1 Decenter(μm)-y', 'S1 Decenter(μm)-abs']},
                    {'kpi': 'OCL1S2', 'title_suffix': 'S2 Decenter(μm)', 'columns': ['S2 Decenter(μm)-x', 'S2 Decenter(μm)-y', 'S2 Decenter(μm)-abs']},
                    {'kpi': 'OCL1tilt', 'title_suffix': 'Tilt(\')', 'columns': ['Tilt(\')-x', 'Tilt(\')-y', 'Tilt(\')-abs']},
                    {'kpi': 'OCL2S1', 'title_suffix': 'S1 Decenter(μm)', 'columns': ['S1 Decenter(μm)-x', 'S1 Decenter(μm)-y', 'S1 Decenter(μm)-abs']},
                    {'kpi': 'OCL2S2', 'title_suffix': 'S2 Decenter(μm)', 'columns': ['S2 Decenter(μm)-x', 'S2 Decenter(μm)-y', 'S2 Decenter(μm)-abs']},
                    {'kpi': 'OCL2tilt', 'title_suffix': 'Tilt(\')', 'columns': ['Tilt(\')-x', 'Tilt(\')-y', 'Tilt(\')-abs']}
                ]
                
                # 根据当前 sheet_name 过滤相关配置
                relevant_configs = []
                if sheet_name == 'OC-L1':
                    relevant_configs = oc_configs[:3]  # 前三个配置对应 OC-L1
                elif sheet_name == 'OC-L2':
                    relevant_configs = oc_configs[3:]  # 后三个配置对应 OC-L2
                
                for config in relevant_configs:
                    # 检查所需的列是否存在
                    missing_cols = [col for col in config['columns'] if col not in filtered_df.columns]
                    if missing_cols:
                        print(f"Warning: Missing columns {missing_cols} in {sheet_name} for {config['kpi']}")
                        continue
                    
                    # 获取 KPI 信息
                    kpi_name = config['kpi']
                    try:
                        kpi_info = kpi_df[kpi_df['KPI'] == kpi_name].iloc[0]
                        tester_name = kpi_info['Tester']
                        usl = kpi_info['USL']
                        lsl = kpi_info['LSL']
                    except IndexError:
                        print(f"Warning: KPI {kpi_name} not found in kpi_mapping. Skipping.")
                        continue

                    all_kpis_set.add(kpi_name)

                    # --- [FIXED] 动态计算 Y 轴范围以确保USL/LSL警戒线始终显示 ---
                    all_relevant_values = []
                    
                    # 收集所有相关的数据点
                    for col in config['columns']:
                        if col in filtered_df.columns:
                            kpi_series = filtered_df[col].dropna().astype(float)
                            if not kpi_series.empty:
                                all_relevant_values.extend([kpi_series.min(), kpi_series.max()])
                    
                    # 将 USL/LSL 添加到范围计算中，确保警戒线在图中可见
                    if pd.notna(usl):
                        all_relevant_values.append(float(usl))
                    if pd.notna(lsl):
                        all_relevant_values.append(float(lsl))

                    y_axis_opts = opts.AxisOpts() # 默认为自动范围
                    if all_relevant_values:
                        y_min_val = min(all_relevant_values)
                        y_max_val = max(all_relevant_values)
                        
                        # 确保即使只有一个值，也添加一些缓冲
                        if y_min_val == y_max_val:
                            # 如果所有值都相同，则基于该值创建一个小缓冲区
                            buffer = abs(y_min_val) * 0.1 if y_min_val != 0 else 0.5
                        else:
                            # 添加 10% 的缓冲区，但最小缓冲要足以显示警戒线
                            diff = y_max_val - y_min_val
                            buffer = diff * 0.1
                        
                        # 确保警戒线位于Y轴范围内
                        final_y_min = y_min_val - buffer if pd.isna(lsl) or lsl >= y_min_val - buffer else min(y_min_val - buffer, float(lsl))
                        final_y_max = y_max_val + buffer if pd.isna(usl) or usl <= y_max_val + buffer else max(y_max_val + buffer, float(usl))
                        
                        y_axis_opts = opts.AxisOpts(min_=final_y_min, max_=final_y_max)

                    # --- [NEW] 计算每个系列的警报等级 ---
                    alert_level_per_series = []
                    for col in config['columns']:
                        if col in filtered_df.columns:
                            series_data = filtered_df[col].dropna().astype(float)
                            if not series_data.empty and pd.notna(usl) and pd.notna(lsl):
                                spec_range = float(usl) - float(lsl)
                                if spec_range > 0:
                                    data_range = series_data.max() - series_data.min()
                                    ratio = data_range / spec_range
                                    if ratio >= 0.2:
                                        alert_level_per_series.append('red')
                                    elif ratio >= 0.1:
                                        alert_level_per_series.append('yellow')
                                    else:
                                        alert_level_per_series.append('normal')
                            else:
                                alert_level_per_series.append('normal')

                    # 根据各系列警报等级确定整体警报等级（红 > 黄 > 正常）
                    if 'red' in alert_level_per_series:
                        alert_level = 'red'
                    elif 'yellow' in alert_level_per_series:
                        alert_level = 'yellow'
                    else:
                        alert_level = 'normal'

                    # --- 步骤 6: 创建 Pyecharts 折线图 ---
                    line_chart = (
                        Line()
                        .add_xaxis(filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist())
                    )
                    
                    # 添加每条线
                    for col in config['columns']:
                        if col in filtered_df.columns:
                            # 计算该列的最大值和最小值 - 【修复】正确处理数据
                            series_data = filtered_df[col].dropna()
                            if not series_data.empty:
                                # 确保数据是数值类型
                                series_data = pd.to_numeric(series_data, errors='coerce')
                                series_data = series_data.dropna()  # 再次去除转换后可能产生的NaN
                                
                                if not series_data.empty:
                                    max_val = series_data.max()
                                    min_val = series_data.min()
                                    max_minus_min = round(max_val - min_val, 2)
                                else:
                                    max_minus_min = "N/A"
                            else:
                                max_minus_min = "N/A"
                            
                            line_chart.add_yaxis(
                                series_name=col,
                                y_axis=filtered_df[col].tolist(),
                                label_opts=opts.LabelOpts(is_show=False),
                                markpoint_opts=opts.MarkPointOpts(
                                    data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")]
                                ),
                            )

                    # --- [FIX] 修复 visualmap_opts 和 markline_opts 的构建逻辑 ---
                    pieces = []
                    if pd.notna(usl):
                        pieces.append({"gt": usl, "color": "#d94e5d"})
                    if pd.notna(lsl):
                        pieces.append({"lt": lsl, "color": "#d94e5d"})
                    if pd.notna(lsl) and pd.notna(usl):
                        pieces.append({"gte": lsl, "lte": usl, "color": "#2f4554"})
                    
                    if pieces:
                        line_chart.set_global_opts(
                            visualmap_opts=opts.VisualMapOpts(
                                is_show=False,
                                type_="piecewise",
                                pieces=pieces,
                                orient="horizontal",
                                pos_left="center",
                                pos_top="bottom",
                            )
                        )

                    mark_line_data = []
                    if pd.notna(usl):
                        mark_line_data.append(opts.MarkLineItem(y=usl, name="USL"))
                    if pd.notna(lsl):
                        mark_line_data.append(opts.MarkLineItem(y=lsl, name="LSL"))
                    
                    if mark_line_data:
                        line_chart.set_series_opts(
                            markline_opts=opts.MarkLineOpts(
                                data=mark_line_data,
                                symbol="none",
                                label_opts=opts.LabelOpts(position="end"),
                                linestyle_opts=opts.LineStyleOpts(type_="dashed")
                            )
                        )

                    # [NEW] 应用Y轴设置
                    line_chart.set_global_opts(yaxis_opts=y_axis_opts)

                    # [NEW] 添加 Graphic 组件来在右上角显示统计信息
                    # 为每个系列计算统计信息
                    chart_graphics = []
                    for idx, col in enumerate(config['columns']):
                        if col in filtered_df.columns:
                            series_data = filtered_df[col].dropna().astype(float)
                            if not series_data.empty:
                                max_val = series_data.max()
                                min_val = series_data.min()
                                max_minus_min = round(max_val - min_val, 2)
                                
                                # 在右上角附近显示文本框，为每条线分配垂直偏移
                                text_offset = idx * 30  # 每个文本框垂直间距30像素
                                
                                graphic_text = {
                                    "type": "text",
                                    "right": 10,
                                    "top": 10 + text_offset,
                                    "z": 100,  # 确保文本在最上层
                                    "style": {
                                        "text": f"{col}: Max-Min={max_minus_min}, USL={usl}, LSL={lsl}",
                                        "textAlign": "right",
                                        "fill": "#000",
                                        "fontSize": 12,
                                        "fontFamily": "PT Sans-Regular"
                                    }
                                }
                                chart_graphics.append(graphic_text)
                    
                    # [NEW] 将图表配置、警报等级存入嵌套字典
                    chart_option_dict = json.loads(line_chart.dump_options())
                    
                    # [MODIFIED] 为每个系列添加maxMinusMin值到chart_option_dict - 确保所有情况都有值
                    if 'series' in chart_option_dict:
                        for idx, series_item in enumerate(chart_option_dict['series']):
                            if idx < len(config['columns']):
                                col = config['columns'][idx]
                                series_data = filtered_df[col].dropna().astype(float)
                                if not series_data.empty:
                                    max_val = series_data.max()
                                    min_val = series_data.min()
                                    max_minus_min = round(max_val - min_val, 2)
                                    # 添加maxMinusMin到series配置
                                    series_item['maxMinusMin'] = max_minus_min
                                else:
                                    series_item['maxMinusMin'] = "N/A"
                    
                    tester_kpi_chart_options[tester_name][kpi_name] = {
                        'chart': chart_option_dict,
                        'alert_level': alert_level
                    }
            else:
                # --- 常规处理其他 sheet ---
                # 步骤 5: 遍历列，为每个KPI生成图表 ---
                for kpi_name in filtered_df.columns:
                    if kpi_name in ['Date', 'Spec']:
                        continue
                    
                    try:
                        kpi_info = kpi_df[kpi_df['KPI'] == kpi_name].iloc[0]
                        tester_name = kpi_info['Tester']
                        usl = kpi_info['USL']
                        lsl = kpi_info['LSL']
                    except IndexError:
                        continue # Skip if KPI not in mapping

                    all_kpis_set.add(kpi_name)

                    # --- [FIXED] 动态计算 Y 轴范围以确保USL/LSL警戒线始终显示 ---
                    kpi_series = filtered_df[kpi_name].dropna().astype(float)
                    
                    all_relevant_values = []
                    if not kpi_series.empty:
                        all_relevant_values.extend([kpi_series.min(), kpi_series.max()])

                    # 将 USL/LSL 添加到范围计算中，确保警戒线在图中可见
                    if pd.notna(usl):
                        all_relevant_values.append(float(usl))
                    if pd.notna(lsl):
                        all_relevant_values.append(float(lsl))

                    y_axis_opts = opts.AxisOpts() # 默认为自动范围
                    if all_relevant_values:
                        y_min_val = min(all_relevant_values)
                        y_max_val = max(all_relevant_values)
                        
                        # 确保即使只有一个值，也添加一些缓冲
                        if y_min_val == y_max_val:
                            # 如果所有值都相同，则基于该值创建一个小缓冲区
                            buffer = abs(y_min_val) * 0.1 if y_min_val != 0 else 0.5
                        else:
                            # 添加 10% 的缓冲区，但最小缓冲要足以显示警戒线
                            diff = y_max_val - y_min_val
                            buffer = diff * 0.1
                        
                        # 确保警戒线位于Y轴范围内
                        final_y_min = y_min_val - buffer if pd.isna(lsl) or lsl >= y_min_val - buffer else min(y_min_val - buffer, float(lsl))
                        final_y_max = y_max_val + buffer if pd.isna(usl) or usl <= y_max_val + buffer else max(y_max_val + buffer, float(usl))
                        
                        y_axis_opts = opts.AxisOpts(min_=final_y_min, max_=final_y_max)

                    # --- [NEW] 计算警报等级 ---
                    alert_level = 'normal'
                    if pd.notna(usl) and pd.notna(lsl) and not kpi_series.empty:
                        spec_range = float(usl) - float(lsl)
                        if spec_range > 0:
                            data_range = kpi_series.max() - kpi_series.min()
                            ratio = data_range / spec_range
                            if ratio >= 0.2:
                                alert_level = 'red'
                            elif ratio >= 0.1:
                                alert_level = 'yellow'

                    # --- 步骤 6: 创建 Pyecharts 折线图 ---
                    # [NEW] 计算Max-Min值 - 【修复】正确处理数据
                    kpi_series = pd.to_numeric(filtered_df[kpi_name], errors='coerce').dropna()
                    if not kpi_series.empty:
                        max_val = kpi_series.max()
                        min_val = kpi_series.min()
                        max_minus_min = round(max_val - min_val, 2)
                    else:
                        max_minus_min = "N/A"

                    line_chart = (
                        Line()
                        .add_xaxis(filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist())
                        .add_yaxis(
                            series_name=kpi_name,
                            y_axis=filtered_df[kpi_name].tolist(),  # 保持原始数据，让前端处理
                            label_opts=opts.LabelOpts(is_show=False),
                            markpoint_opts=opts.MarkPointOpts(
                                data=[opts.MarkPointItem(type_="max"), opts.MarkPointItem(type_="min")]
                            ),
                        )
                    )
                    
                    # 添加文本框显示统计信息
                    text_content = f"{kpi_name}\nMax-Min: {max_minus_min}"
                    if pd.notna(usl):
                        text_content += f"\nUSL: {usl}"
                    if pd.notna(lsl):
                        text_content += f"\nLSL: {lsl}"
                    
                    # --- [FIX] 修复 visualmap_opts 和 markline_opts 的构建逻辑 ---
                    pieces = []
                    if pd.notna(usl):
                        pieces.append({"gt": usl, "color": "#d94e5d"})
                    if pd.notna(lsl):
                        pieces.append({"lt": lsl, "color": "#d94e5d"})
                    if pd.notna(lsl) and pd.notna(usl):
                        pieces.append({"gte": lsl, "lte": usl, "color": "#2f4554"})
                    
                    if pieces:
                        line_chart.set_global_opts(
                            visualmap_opts=opts.VisualMapOpts(
                                is_show=False,
                                type_="piecewise",
                                pieces=pieces,
                                orient="horizontal",
                                pos_left="center",
                                pos_top="bottom",
                            )
                        )

                    mark_line_data = []
                    if pd.notna(usl):
                        mark_line_data.append(opts.MarkLineItem(y=usl, name="USL"))
                    if pd.notna(lsl):
                        mark_line_data.append(opts.MarkLineItem(y=lsl, name="LSL"))
                    
                    if mark_line_data:
                        line_chart.set_series_opts(
                            markline_opts=opts.MarkLineOpts(
                                data=mark_line_data,
                                symbol="none",
                                label_opts=opts.LabelOpts(position="end"),
                                linestyle_opts=opts.LineStyleOpts(type_="dashed")
                            )
                        )

                    # [NEW] 应用Y轴设置
                    line_chart.set_global_opts(yaxis_opts=y_axis_opts)

                    # [NEW] 将图表配置、警报等级存入嵌套字典
                    # 在 visualization 方法中，修改 chart_option_dict 的构建逻辑
                    chart_option_dict = json.loads(line_chart.dump_options())
                    # 确保所有值都是有效的 JSON 类型
                    for key, value in chart_option_dict.items():
                        if isinstance(value, dict):
                            # 递归处理嵌套字典
                            pass
                        elif isinstance(value, list):
                            # 处理列表中的 None 值
                            chart_option_dict[key] = [v if v is not None else "" for v in value]
                        elif value is None:
                            chart_option_dict[key] = ""
                    
                    # [MODIFIED] 为常规处理部分也添加maxMinusMin到series
                    if 'series' in chart_option_dict and len(chart_option_dict['series']) > 0:
                        chart_option_dict['series'][0]['maxMinusMin'] = max_minus_min
                    
                    tester_kpi_chart_options[tester_name][kpi_name] = {
                        'chart': chart_option_dict,
                        'alert_level': alert_level
                    }

        if not tester_kpi_chart_options:
            raise ValueError("No data to visualize for the selected date range.")

        # --- 步骤 7: 使用 Jinja2 模板进行渲染 ---

        # 7a: [FIX] 硬编码 ECharts 的 JS 依赖项，绕过 pyecharts 的自动依赖管理
        # 我们直接提供一个稳定、公开的 CDN URL，确保浏览器能加载到库文件。
        js_dependencies = ["https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"]

        # 7b: 准备模板需要的额外变量
        template_vars = {
            "js_dependencies": js_dependencies,
            "chart_data": tester_kpi_chart_options,
        }

        # 7c: 配置并渲染 Jinja2 模板
        template_path = os.path.join(os.path.dirname(__file__), '..', 'templates')
        env = Environment(loader=FileSystemLoader(template_path))
        template = env.get_template("visualization_template.html")
        html_content = template.render(**template_vars)

        # 7d: 写入 HTML 文件
        with open(output_html_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        # 返回图表数据和日期范围，以便在 dataprocessinggroup.py 中使用
        return tester_kpi_chart_options, start_date, end_date

class LomaVisRoutineInspection(VisRoutineInspection):
    pass

class HummingbirdVisRoutineInspection(VisRoutineInspection):
    pass