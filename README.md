Nuxt/Flask/NGINX boilerplate
============================

Useful to quickly get started on building Flask apps with modern frontend practices.

To re-initialize the frontend folder from scratch:

- `rm -rf frontend/`
- `docker-compose run --rm frontend yarn create nuxt-app .`

Then add the following block to `frontend/nuxt.config.js`:

```js
  server: {
    socket: '/run/nuxt.sock'
  },
```
