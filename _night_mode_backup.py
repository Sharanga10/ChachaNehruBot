import time
import datetime
from main import run_bot as post_tweet  # ✅ Correct import

# IST = UTC + 5:30
IST_OFFSET = datetime.timedelta(hours=5, minutes=30)
END_TIME_IST = datetime.datetime.combine(
    datetime.date.today(), datetime.time(hour=6, minute=10)
)

def get_current_ist():
    return datetime.datetime.utcnow() + IST_OFFSET

def run_night_mode():
    print("🌙 Night Mode: Starting tweet loop till 6:10 AM IST...\n")
    while True:
        now_ist = get_current_ist()
        print(f"⏰ Current IST Time: {now_ist.strftime('%H:%M:%S')}")

        if now_ist >= END_TIME_IST:
            print("✅ 6:10 AM reached. Night Mode complete. Exiting...")
            break

        try:
            print("🚀 Posting tweet via Chacha Nehru Bot...")
            post_tweet()
        except Exception as e:
            print(f"❌ Error posting tweet: {e}")

        print("⏳ Sleeping for 20 minutes...\n")
        time.sleep(20 * 60)  # 20 minutes

if __name__ == "__main__":
    run_night_mode()