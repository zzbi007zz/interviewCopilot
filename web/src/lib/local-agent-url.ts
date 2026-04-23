const LOCAL_HOSTS = new Set(['127.0.0.1', 'localhost'])

export const buildLocalAgentWebSocketUrl = (port: number, host = '127.0.0.1'): string => {
  const normalizedHost = host.trim().toLowerCase()
  if (!LOCAL_HOSTS.has(normalizedHost)) {
    throw new Error('Local agent websocket host must be localhost or 127.0.0.1')
  }

  if (!Number.isInteger(port) || port < 1 || port > 65535) {
    throw new Error('Local agent websocket port must be an integer between 1 and 65535')
  }

  return `ws://${normalizedHost}:${port}`
}
