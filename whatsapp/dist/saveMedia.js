import fs from "fs";
import path from "path";
import { downloadMediaMessage } from "baileys";
export async function saveMedia(msg, sock, extension) {
    const buffer = await downloadMediaMessage(msg, "buffer", {}, {
        logger: console,
        reuploadRequest: sock.updateMediaMessage,
    });
    const filename = `${Date.now()}.${extension}`;
    const filepath = path.join("uploads", filename);
    fs.mkdirSync("uploads", { recursive: true });
    fs.writeFileSync(filepath, buffer);
    return path.resolve(filepath);
}
