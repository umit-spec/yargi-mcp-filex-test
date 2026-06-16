"""
PRO MCP tek-test: mcp-remote üzerinden TOKEN GÖRMEDEN 1 HGK kararı çek.

GÜVENLİK SÖZLEŞMESİ (kesin):
  - Bu kod token / refresh_token / client_secret / .mcp-auth dosyalarını
    OKUMAZ, YAZMAZ, YAZDIRMAZ. Hiçbir yerde token'a dokunmaz.
  - OAuth + 5 dakikalık token tazeleme tamamen mcp-remote subprocess'inde kalır.
  - Biz yalnızca stdio üzerinden MCP tool çağrısı yapar, karar verisini (gizli
    DEĞİL) alırız.

KAPSAM (bugün): initialize + tools/list (raporla) + 1 ictihat_getir → results/pro_raw/.
  Toplu crawler YOK, rate-limit YOK, cron YOK, Silver/raw_capture bağlama YOK.
"""
import asyncio
import json
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

URL = "https://yargi.betaspacestudio.com/mcp"
OUT = Path(__file__).parent.parent / "results" / "pro_raw"
HGK_DOC_ID = "233351200"  # HGK · ihalenin feshi · E.2014/1077 K.2016/584

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def extract_text(result) -> str:
    parts = []
    for c in getattr(result, "content", []) or []:
        t = getattr(c, "text", None)
        if t:
            parts.append(t)
    return "\n".join(parts)


async def main():
    params = StdioServerParameters(
        command="npx.cmd",
        args=["-y", "mcp-remote", URL],
    )
    print(f"[..] mcp-remote başlatılıyor (token mcp-remote'ta, kod görmez)…")
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await asyncio.wait_for(session.initialize(), timeout=120)
            print("[OK] initialize tamam")

            tools = await asyncio.wait_for(session.list_tools(), timeout=60)
            names = [t.name for t in tools.tools]
            print(f"[OK] tools/list: {len(names)} araç")
            for n in names:
                print("   -", n)

            print(f"\n[..] tek tool call: ictihat_getir(documentId={HGK_DOC_ID})")
            res = await asyncio.wait_for(
                session.call_tool("ictihat_getir", {"documentId": HGK_DOC_ID}),
                timeout=180,
            )
            text = extract_text(res)
            print(f"[OK] yanıt: {len(text)} karakter")

            OUT.mkdir(parents=True, exist_ok=True)
            outfile = OUT / f"pro_test_{HGK_DOC_ID}.json"
            try:
                payload = json.loads(text)
            except Exception:
                payload = {"raw_text": text}
            outfile.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[OK] yazıldı: {outfile}")


if __name__ == "__main__":
    asyncio.run(main())
