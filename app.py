from flask import Flask, render_template, Response
from database.db import init_db, get_violations
import threading
from detection.detect import detect_violations, detect_violations_stream

app = Flask(__name__)

@app.route("/")
def index():
    data = get_violations()

    total_violations = len(data)

    # ✅ SAFE fine calculation (no crash)
    total_fine = sum([row[4] if len(row) > 4 else 0 for row in data]) if data else 0

    # 📊 Chart data
    times = [row[2][:10] for row in data]
    chart_data = {}
    for t in times:
        chart_data[t] = chart_data.get(t, 0) + 1

    labels = list(chart_data.keys())
    values = list(chart_data.values())

    return render_template("index.html",
                           data=data,
                           total_violations=total_violations,
                           total_fine=total_fine,
                           labels=labels,
                           values=values)


# 🔥 VIDEO STREAM ROUTE
@app.route('/video_feed')
def video_feed():
    return Response(detect_violations_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    init_db()

    # 🔥 OPTIONAL: run detection in background
    # (for saving images automatically)
    t = threading.Thread(target=detect_violations)
    t.daemon = True
    t.start()

    app.run(debug=True, use_reloader=False)