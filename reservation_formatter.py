import google.generativeai as genai
from icalendar import Calendar, Event
import datetime
from pathlib import Path
import json
from PIL import Image
from config import get_api_key

class ReservationFormatter:
    def __init__(self):
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro-vision')

    def analyze_image(self, image_path):
        """画像の解析"""
        try:
            # 画像を読み込み
            img = Image.open(image_path)
            
            # プロンプトの作成
            prompt = """
以下の予約画面のスクリーンショットから情報を抽出し、正確なJSONフォーマットで返してください。

必要な情報:
1. reservation_number (予約番号)
2. date (来店日, YYYY-MM-DD形式)
3. time (来店時間, 開始と終了を含む)
   - start_time (HH:MM形式)
   - end_time (HH:MM形式)
4. customer (顧客情報)
   - name (漢字)
   - name_kana (フリガナ)
   - is_assigned (指名予約かどうか, true/false)
5. payment (料金情報)
   - amount (クーポン金額)
   - points_used (使用ポイント)
   - final_amount (最終支払額)
6. type (予約種別: "医療-予約用"、"エクシア会員"、"エクシア新規"のいずれか)

レスポンスは必ず有効なJSON形式で返してください。
"""

            # Geminiによる解析
            response = self.model.generate_content([prompt, img])
            
            # レスポンスのパース
            try:
                # JSON文字列の抽出（余分なテキストがある場合に対応）
                json_str = response.text
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0]
                elif "```" in json_str:
                    json_str = json_str.split("```")[1]
                
                result = json.loads(json_str.strip())
                print("解析結果:", json.dumps(result, indent=2, ensure_ascii=False))
                return result
            
            except json.JSONDecodeError as e:
                print(f"JSONパースエラー: {e}")
                print("Geminiレスポンス:", response.text)
                raise

        except Exception as e:
            print(f"画像解析エラー: {str(e)}")
            raise

    def create_calendar_event(self, info):
        """カレンダーイベントの作成"""
        try:
            event = Event()
            
            # 日時の設定
            date = datetime.datetime.strptime(info['date'], '%Y-%m-%d').date()
            start_time = datetime.datetime.strptime(info['time']['start_time'], '%H:%M').time()
            end_time = datetime.datetime.strptime(info['time']['end_time'], '%H:%M').time()
            
            start_dt = datetime.datetime.combine(date, start_time)
            end_dt = datetime.datetime.combine(date, end_time)
            
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            
            # タイトルの設定
            title_parts = []
            if info['customer']['is_assigned']:
                title_parts.append("【指名】")
            title_parts.append(f"{info['customer']['name']}（{info['customer']['name_kana']}）")
            event.add('summary', "".join(title_parts))
            
            # 説明文の設定
            description = [
                f"予約番号: {info['reservation_number']}",
                f"来店時間: {info['time']['start_time']}～{info['time']['end_time']}",
                f"顧客名: {info['customer']['name']}",
                f"フリガナ: {info['customer']['name_kana']}",
                f"指名: {'あり' if info['customer']['is_assigned'] else 'なし'}",
                f"料金: {info['payment']['amount']}円",
                f"使用ポイント: {info['payment']['points_used']}ポイント",
                f"お支払い: {info['payment']['final_amount']}円"
            ]
            
            event.add('description', "\n".join(description))
            
            # アラート設定（30分前）
            from datetime import timedelta
            alarm = Event()
            alarm.add('action', 'DISPLAY')
            alarm.add('trigger', timedelta(minutes=-30))
            event.add_component(alarm)
            
            return event

        except Exception as e:
            print(f"イベント作成エラー: {str(e)}")
            raise

    def process(self, image_path: Path, output_path: Path):
        """メイン処理"""
        try:
            print(f"処理を開始: {image_path}")
            
            # 画像の解析
            info = self.analyze_image(image_path)
            print("画像解析完了")
            
            # カレンダーの作成
            cal = Calendar()
            event = self.create_calendar_event(info)
            cal.add_component(event)
            
            # ファイルの保存
            with open(output_path, 'wb') as f:
                f.write(cal.to_ical())
            print(f"iCalendarファイル作成完了: {output_path}")
            
            return True, info['type']
            
        except Exception as e:
            print(f"処理エラー: {str(e)}")
            return False, None