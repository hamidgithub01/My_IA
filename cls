[1mdiff --git a/frontend/services/prediction_service.py b/frontend/services/prediction_service.py[m
[1mindex 971a3d4..3506293 100644[m
[1m--- a/frontend/services/prediction_service.py[m
[1m+++ b/frontend/services/prediction_service.py[m
[36m@@ -1560,6 +1560,7 @@[m [mdef generate_expense_forecast([m
     days=30,[m
     target_name=DEFAULT_TARGET_NAME,[m
     registry_dir=None,[m
[32m+[m[32m    value_key='Predicted_Expense',[m
 ):[m
     """[m
     Generate a multi-day expense forecast.[m
[36m@@ -2025,7 +2026,7 @@[m [mdef generate_expense_forecast([m
             'Date':[m
                 forecast_date,[m
 [m
[31m-            'Predicted_Expense':[m
[32m+[m[32m            value_key:[m
                 prediction,[m
         })[m
 [m
[36m@@ -2055,6 +2056,7 @@[m [mdef load_predictions_page_data([m
     days=30,[m
     target_name=DEFAULT_TARGET_NAME,[m
     registry_dir=None,[m
[32m+[m[32m    value_key='Predicted_Expense',[m
 ):[m
     """[m
     Load all data required by the Predictions page.[m
[36m@@ -2064,6 +2066,7 @@[m [mdef load_predictions_page_data([m
         days=days,[m
         target_name=target_name,[m
         registry_dir=registry_dir,[m
[32m+[m[32m        value_key=value_key,[m
     )[m
 [m
     forecast = forecast_result.get([m
[36m@@ -2074,7 +2077,7 @@[m [mdef load_predictions_page_data([m
     values = [[m
         float([m
             row.get([m
[31m-                'Predicted_Expense',[m
[32m+[m[32m                value_key,[m
                 0.0,[m
             )[m
         )[m
