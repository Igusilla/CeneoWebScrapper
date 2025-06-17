import os
import io
from flask import send_file, Response
from app.managers.opinion_manager import OpinionManager

class DownloadManager:
    @staticmethod
    def download(product_id, filetype, app_root):
        df = OpinionManager.to_dataframe(product_id)
        if filetype == "json":
            path = os.path.join(app_root, "data", "opinions", f"{product_id}.json")
            return send_file(
                path,
                mimetype="application/json",
                as_attachment=True,
                download_name=f"{product_id}.json"
            )
        elif filetype == "csv":
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename={product_id}.csv"}
            )
        elif filetype == "xlsx":
            output = io.BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": f"attachment;filename={product_id}.xlsx"}
            )
        else:
            return "Nieobsługiwany format", 400