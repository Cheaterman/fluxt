export interface Message {
  id: string
  date: string
  author: string
  text: string
}

// FIXME: See if this could be simplified using advice from https://nuxt.com/docs/getting-started/data-fetching#consuming-sse-server-sent-events-via-post-request
export default async function() {
  const { $api } = useNuxtApp()
  const messages = ref<Message[]>([])
  let stream: ReadableStream
  let reader: ReadableStreamDefaultReader<Uint8Array>

  onMounted(async () => {
    stream = await $api<typeof stream>('/messages', {
      responseType: 'stream',
    })
    reader = stream.getReader()
    const decoder = new TextDecoder()
    const DATA_PREFIX = 'data: '

    while (true) {
      let result: ReadableStreamReadResult<Uint8Array>

      try {
        result = await reader.read()
      }
      catch(error) {
        if (
          !(error instanceof TypeError)
          || error.message !== 'Releasing lock'
        ) {
          reader.releaseLock()
        }
        break
      }

      if (result.done) {
        reader.releaseLock()
        break
      }

      const data = decoder.decode(result.value)

      for (const line of data.split('\n')) {
        if (!line.startsWith(DATA_PREFIX)) {
          continue
        }

        messages.value.push(JSON.parse(line.slice(DATA_PREFIX.length)))
      }
    }
  })

  onUnmounted(async () => {
    reader?.releaseLock()
    await stream?.cancel()
  })

  return {
    data: messages
  }
}
