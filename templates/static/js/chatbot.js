const res = await fetch("{{ url_for('chat_api') }}", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "X-Requested-With": "XMLHttpRequest"
  },
  body: JSON.stringify({ message })
});
