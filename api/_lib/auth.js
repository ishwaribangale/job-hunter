import { verifyToken } from "@clerk/backend";

export async function requireUser(req) {
  const authHeader = req.headers.authorization || "";
  const token = authHeader.startsWith("Bearer ") ? authHeader.slice(7) : null;

  if (!token) {
    return { error: { status: 401, message: "Missing auth token" } };
  }

  try {
    const payload = await verifyToken(token, {
      secretKey: process.env.CLERK_SECRET_KEY,
    });
    return { userId: payload.sub };
  } catch (error) {
    return { error: { status: 401, message: "Invalid auth token" } };
  }
}
