import os
import json

class LeaderboardManager:
    def __init__(self, filepath="leaderboard.json"):
        self.filepath = filepath
        self.data = self.Load()

    def Load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                try:
                    return json.load(f)
                except:
                    return []
        return []

    def Update(self, name, score):
        currentPlay = {"name": name, "score": score}
        self.data.append(currentPlay)
        self.data.sort(key=lambda x: x["score"], reverse=True)
        
        rank = self.data.index(currentPlay) + 1
        
        with open(self.filepath, "w") as f:
            json.dump(self.data, f)
            
        return rank

    def get_top_scores(self, limit=5):
        return self.data[:limit]

    def get_high_score(self):
        return self.data[0]["score"] if len(self.data) > 0 else 0