import { UploadResponse } from "../type";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

export const documentService = {
  async upload(file: File): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/documents/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error("Failed to upload document");
    }

    const json = (await response.json()) as UploadResponse;
    return json;
  },
};
