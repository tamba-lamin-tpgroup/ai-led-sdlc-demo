// Module-level promise cache — prevents duplicate fetches on SPA navigation.
const cache = new Map<string, Promise<unknown>>();

export function cachedFetch<T>(key: string, fn: () => Promise<T>): Promise<T> {
  if (!cache.has(key)) {
    cache.set(key, fn().catch((err) => {
      cache.delete(key);
      throw err;
    }));
  }
  return cache.get(key) as Promise<T>;
}

export function invalidateCache(key?: string): void {
  if (key) {
    cache.delete(key);
  } else {
    cache.clear();
  }
}
