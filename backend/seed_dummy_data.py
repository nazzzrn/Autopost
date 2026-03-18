import sqlite3
import uuid
import random
from datetime import datetime, timezone, timedelta

def seed():
    conn = sqlite3.connect("autopost.db")
    c = conn.cursor()
    
    platforms = ["instagram", "facebook"]
    
    for i in range(5):
        post_id = str(uuid.uuid4())
        analytics_id = str(uuid.uuid4())
        platform = random.choice(platforms)
        
        # Random past date within last 14 days
        past_time = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14))
        past_time_str = past_time.isoformat()
        
        # Insert post without platform_post_id, so the Refresh API skips it and preserves our dummy data!
        c.execute('''
            INSERT INTO posts (id, platform, caption, image_url, status, published_time, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (post_id, platform, f"✨ Exploring new horizons with dummy placeholder post {i+1}! #AI #Innovation 🚀", 
              "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?auto=format&fit=crop&w=400&q=80", 
              "published", past_time_str, past_time_str, past_time_str))
              
        # Insert analytics
        reach = random.randint(100, 800)
        impressions = reach + random.randint(10, 200)
        likes = random.randint(1, 10)
        comments = random.randint(0, 5)
        engagement = likes + comments
        eng_rate = (engagement / reach) * 100 if reach > 0 else 0.0
        
        c.execute('''
            INSERT INTO analytics (id, post_id, reach, impressions, engagement, likes, comments, engagement_rate, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (analytics_id, post_id, reach, impressions, engagement, likes, comments, eng_rate, past_time_str))
        
    conn.commit()
    conn.close()
    print("Dummy data seeded successfully!")

if __name__ == "__main__":
    seed()
