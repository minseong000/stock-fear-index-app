from flask import Flask, request, jsonify
import yfinance as yf

app = Flask(__name__)

def calculate_fear_index(ticker):
    try:
        stock = yf.Ticker(ticker, validate=False)  # validate 옵션 비활성화
        hist = stock.history(period="6mo")

        if hist.empty:
            return {"error": "주가 데이터를 가져오지 못했습니다. 유효한 티커인지 확인하세요."}

        try:
            info = stock.info
        except Exception as e:
            return {"error": f"기업 정보 불러오기 실패: {str(e)}"}

        current_price = info.get("currentPrice") or hist["Close"][-1]
        ma60 = hist["Close"].rolling(60).mean().iloc[-1]
        low_52 = info.get("fiftyTwoWeekLow")
        short_ratio = info.get("shortRatio", 0)
        volume_avg = info.get("averageVolume", 1)
        volume_today = hist["Volume"].iloc[-1]
        iv = info.get("impliedVolatility", 0.3) * 100

        score_momentum = max(0, min(100, 50 + (current_price - ma60) / ma60 * 100))
        score_low52 = max(0, min(100, 100 - ((current_price - low_52) / current_price * 100)))
        score_volume = max(0, min(100, 50 + (volume_today - volume_avg) / volume_avg * 100))
        score_short = max(0, min(100, 100 - short_ratio * 10))
        score_iv = max(0, min(100, 100 - iv))

        scores = [score_momentum, score_low52, score_volume, score_short, score_iv]
        avg_score = round(sum(scores) / len(scores))

        if avg_score < 25:
            status = "극단적 공포"
        elif avg_score < 50:
            status = "공포"
        elif avg_score < 75:
            status = "중립"
        else:
            status = "탐욕"

        return {
            "ticker": ticker.upper(),
            "name": info.get("shortName", "Unknown"),
            "score": avg_score,
            "status": status,
            "details": [
                {"label": "60일 평균 대비", "value": f"{(current_price - ma60) / ma60 * 100:.1f}%"},
                {"label": "52주 저가 근접도", "value": f"{(current_price - low_52) / current_price * 100:.1f}%"},
                {"label": "공매도 비율(Short Ratio)", "value": f"{short_ratio:.2f}"},
                {"label": "거래량 변화율", "value": f"{(volume_today - volume_avg) / volume_avg * 100:.1f}%"},
                {"label": "내재 변동성(IV)", "value": f"{iv:.1f}%"}
            ]
        }

    except Exception as e:
        return {"error": f"예상치 못한 오류: {str(e)}"}

@app.route('/api/fear-index', methods=['GET'])
def fear_index():
    ticker = request.args.get("ticker")
    if not ticker:
        return jsonify({"error": "ticker is required"}), 400

    data = calculate_fear_index(ticker)
    if "error" in data:
        return jsonify(data), 500
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)

