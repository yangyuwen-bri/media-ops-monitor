import pandas as pd
import os

# Define file paths
BASE_DIR = "/Users/yuwen/work/XinHuaData"
MAIN_EXCEL = os.path.join(BASE_DIR, "信源监测_20251218_20251218171646352.xlsx")
DATA_DIR = os.path.join(BASE_DIR, "data")
BILI_CSV = os.path.join(DATA_DIR, "xinhua_bili.csv")
RED_CSV = os.path.join(DATA_DIR, "xinhua_red.csv")
WX_CSV = os.path.join(DATA_DIR, "xinhua_wx.csv")

OUTPUT_EXCEL = os.path.join(BASE_DIR, "信源监测_Updated.xlsx")

def clean_url(url):
    """Simple URL cleaner to help matching."""
    if not isinstance(url, str):
        return ""
    return url.strip()

def merge_data():
    print(f"Loading main data from {MAIN_EXCEL}...")
    try:
        df_main = pd.read_excel(MAIN_EXCEL)
    except FileNotFoundError:
        print("Main Excel file not found.")
        return

    # Load back-trace data
    print("Loading back-trace CSVs...")
    try:
        df_bili = pd.read_csv(BILI_CSV)
        df_red = pd.read_csv(RED_CSV)
        df_wx = pd.read_csv(WX_CSV)
    except Exception as e:
        print(f"Error loading CSVs: {e}")
        return

    # Create lookups for faster access and TRACKING matches
    matched_urls = set()
    
    # Pre-process main df to build index of existing articles
    existing_urls = set()
    existing_titles = set()
    for _, row in df_main.iterrows():
        if pd.notna(row['原文链接']):
            existing_urls.add(clean_url(row['原文链接']))
        if pd.notna(row['标题']):
            existing_titles.add(str(row['标题']).strip())

    # Build maps for the CSVs to easily access data
    # We will use these maps for keys
    bili_records = df_bili.to_dict('records')
    red_records = df_red.to_dict('records')
    wx_records = df_wx.to_dict('records')

    # Calculate valid time range from main data
    if '发布时间' in df_main.columns:
        df_main['发布时间'] = pd.to_datetime(df_main['发布时间'])
        min_date = df_main['发布时间'].min()
        max_date = df_main['发布时间'].max()
        print(f"Main data time range: {min_date} to {max_date}")
    else:
        print("Warning: No '发布时间' in main data. Skipping time filtering.")
        min_date = pd.Timestamp.min
        max_date = pd.Timestamp.max

    def is_in_range(date_str):
        try:
            d = pd.to_datetime(date_str)
            return min_date <= d <= max_date
        except:
            return False

    new_rows = []
    updates_count = 0

    # 1. UPDATE PHASE: Iterate existing main data
    for index, row in df_main.iterrows():
        url = clean_url(row['原文链接'])
        title = str(row['标题']).strip()
        platform = str(row['发布平台'])
        
        # Check Bili (Update)
        if 'B站' in platform or 'bilibili' in url:
            for item in bili_records:
                b_url = clean_url(item.get('url'))
                b_title = str(item.get('title')).strip()
                if (url and b_url == url) or (title and b_title == title):
                    # Match found
                    df_main.at[index, '阅读数'] = item.get('read_count', 0)
                    df_main.at[index, '点赞数'] = item.get('like_count', 0)
                    df_main.at[index, '评论数'] = item.get('comment_count', 0)
                    df_main.at[index, '转发数'] = item.get('share_count', 0)
                    updates_count += 1
                    matched_urls.add(b_url)
                    matched_urls.add(b_title) # Track title as "id" too effectively
                    item['_matched'] = True
                    break

        # Check Red (Update)
        elif '小红书' in platform or 'xiaohongshu' in url:
            for item in red_records:
                r_url = clean_url(item.get('url'))
                if url and r_url == url:
                    df_main.at[index, '阅读数'] = item.get('num_read', 0)
                    df_main.at[index, '点赞数'] = item.get('num_like', 0)
                    df_main.at[index, '评论数'] = item.get('num_comment', 0)
                    df_main.at[index, '转发数'] = item.get('num_repost', 0)
                    updates_count += 1
                    matched_urls.add(r_url)
                    item['_matched'] = True
                    break
        
        # Check WeChat (Update)
        elif '微信' in platform or 'weixin' in url:
            for item in wx_records:
                w_url = clean_url(item.get('url'))
                w_title = str(item.get('title')).strip()
                if (url and w_url == url) or (title and w_title == title):
                    df_main.at[index, '阅读数'] = item.get('readnum', 0)
                    df_main.at[index, '点赞数'] = item.get('likenum', 0)
                    df_main.at[index, '转发数'] = item.get('share_num', 0)
                    updates_count += 1
                    matched_urls.add(w_url)
                    matched_urls.add(w_title)
                    item['_matched'] = True
                    break

    # 2. APPEND PHASE: Check for unmatched CSV records with DATE FILTER
    print("Checking for new records to append (within time range)...")
    
    # Append Bilibili
    for item in bili_records:
        if not item.get('_matched'):
            # Double check against existing sets (in case main df had it but we missed mapping logic)
            b_url = clean_url(item.get('url'))
            b_title = str(item.get('title')).strip()
            # Date Check
            b_time = item.get('publish_time')
            if not is_in_range(b_time):
                continue
                
            if b_url not in existing_urls and b_title not in existing_titles:
                new_row = {
                    '发布平台': 'B站',
                    '标题': item.get('title'),
                    '原文链接': item.get('url'),
                    '发布时间': b_time,
                    '阅读数': item.get('read_count', 0),
                    '点赞数': item.get('like_count', 0),
                    '评论数': item.get('comment_count', 0),
                    '转发数': item.get('share_count', 0),
                    '摘要': str(item.get('content', ''))[:100] if pd.notna(item.get('content')) else '', # Content extract, safe handle
                    '作者': item.get('author_name', '新华网'),
                }
                new_rows.append(new_row)

    # Append Red
    for item in red_records:
        if not item.get('_matched'):
            r_url = clean_url(item.get('url'))
            # Date Check
            r_time = item.get('创建时间')
            if not is_in_range(r_time):
                continue

            if r_url not in existing_urls:
                new_row = {
                    '发布平台': '小红书',
                    '标题': '小红书笔记', # Fallback
                    '原文链接': item.get('url'),
                    '发布时间': r_time, # Use create time
                    '阅读数': item.get('num_read', 0),
                    '点赞数': item.get('num_like', 0),
                    '评论数': item.get('num_comment', 0),
                    '转发数': item.get('num_repost', 0),
                }
                new_rows.append(new_row)

    # Append WeChat
    for item in wx_records:
        if not item.get('_matched'):
            w_url = clean_url(item.get('url'))
            w_title = str(item.get('title')).strip()
            # Date Check
            w_time = item.get('posttime')
            if not is_in_range(w_time):
                continue

            if w_url not in existing_urls and w_title not in existing_titles:
                new_row = {
                    '发布平台': '微信',
                    '标题': item.get('title'),
                    '原文链接': item.get('url'),
                    '发布时间': w_time,
                    '阅读数': item.get('readnum', 0),
                    '点赞数': item.get('likenum', 0),
                    '转发数': item.get('share_num', 0),
                    '评论数': 0, # Metric often missing in Wx export
                    '作者': item.get('author')
                }
                new_rows.append(new_row)

    print(f"Data merge complete. Updated {updates_count} rows.")
    print(f"Found {len(new_rows)} new rows to append.")
    
    if new_rows:
        df_new = pd.DataFrame(new_rows)
        # Identify columns in main but not in new (e.g. '情感属性')
        # We should fill them with default
        for col in df_main.columns:
            if col not in df_new.columns:
                df_new[col] = None 
                # Optional: Simple heuristic for sentiment? For now leave matching empty or '中性'
                if col == '情感属性':
                    df_new[col] = '中性' # Default to Neutral for safe display

        # Concatenate
        df_final = pd.concat([df_main, df_new], ignore_index=True)
    else:
        df_final = df_main
    
    # Save
    df_final.to_excel(OUTPUT_EXCEL, index=False)
    print(f"Saved updated file to: {OUTPUT_EXCEL}")

if __name__ == "__main__":
    merge_data()
