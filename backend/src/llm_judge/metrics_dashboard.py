class JudgeMetricsDashboard:
    """Dashboard des performances du Judge"""
    
    def show_metrics(self):
        """Affiche les métriques clés"""
        print("📊 MÉTRIQUES JUDGE")
        print(f"   Précision globale: {self.accuracy:.1%}")
        print(f"   APPROVE corrects: {self.approve_correct}/{self.approve_total}")
        print(f"   REJECT corrects: {self.reject_correct}/{self.reject_total}")
        print(f"   Temps moyen d'évaluation: {self.avg_time:.2f}s")