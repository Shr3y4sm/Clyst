try:
	from app import app
except Exception as e:
	# Print full traceback to the stdout logs so Vercel shows it
	import traceback
	traceback.print_exc()
	# Provide a minimal fallback app so the function returns a 500 with guidance
	from flask import Flask, Response
	app = Flask(__name__)

	@app.route("/")
	def _import_error():
		return Response("Import error during app startup. Check deployment logs for traceback.", status=500)
