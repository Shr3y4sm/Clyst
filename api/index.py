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

# Expose a top-level WSGI application and a handler for Vercel's runtime detection.
try:
	application = app
except NameError:
	from flask import Flask
	application = Flask(__name__)

def handler(environ, start_response):
	"""WSGI handler wrapper for Vercel."""
	return application.wsgi_app(environ, start_response)

# Ensure `app` and `application` names exist at module level for Vercel static detection
try:
	app  # noqa: F821
except NameError:
	app = application

try:
	application  # noqa: F821
except NameError:
	application = app
