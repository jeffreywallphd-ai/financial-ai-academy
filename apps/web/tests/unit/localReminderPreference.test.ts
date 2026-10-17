import { describe, expect, it } from "vitest";

import {
  LOCAL_REMINDER_STORAGE_KEY,
  LocalReminderPreferenceError,
  canonicalIntegrity,
  defaultLocalReminderPreference,
  exportLocalReminderPreference,
  readLocalReminderPreference,
  replaceLocalReminderPreference,
  resetLocalReminderPreference,
} from "../../src/platform/reminders/localReminderPreference";


const START = "2026-10-17T23:00:00Z";

class MemoryStorage {
  values = new Map<string, string>();
  reads = 0;
  writes = 0;

  getItem(key: string) {
    this.reads += 1;
    return this.values.get(key) ?? null;
  }

  setItem(key: string, value: string) {
    this.writes += 1;
    this.values.set(key, value);
  }
}

describe("local learning-reminder preference", () => {
  it("projects a safe off default without writing on read", async () => {
    const storage = new MemoryStorage();
    const result = await readLocalReminderPreference(storage, START);
    expect(result.status).toBe("absent");
    expect(result.envelope).toMatchObject({
      schema_version: "1.0.0",
      revision: 1,
      reminder_mode: "off",
      updated_at: START,
      changes: [],
    });
    expect(result.envelope.integrity_code).toMatch(/^[a-f0-9]{64}$/);
    expect(storage.reads).toBe(1);
    expect(storage.writes).toBe(0);
  });

  it("replaces and resets one complete local envelope", async () => {
    const storage = new MemoryStorage();
    const initial = await defaultLocalReminderPreference(START);
    const enabled = await replaceLocalReminderPreference(
      storage,
      initial,
      "in_app_when_available",
      "2026-10-17T23:01:00Z",
    );
    expect(enabled.revision).toBe(2);
    expect(enabled.reminder_mode).toBe("in_app_when_available");
    expect(storage.writes).toBe(1);
    const stored = await readLocalReminderPreference(storage, START);
    expect(stored).toEqual({ status: "ready", envelope: enabled });

    const reset = await resetLocalReminderPreference(
      storage,
      enabled,
      "2026-10-17T23:02:00Z",
    );
    expect(reset.revision).toBe(3);
    expect(reset.reminder_mode).toBe("off");
    expect(reset.changes.map((change) => change.operation)).toEqual([
      "replace_preference",
      "reset_preference",
    ]);
    expect(storage.writes).toBe(2);
  });

  it("retains only the newest one hundred non-content summaries", async () => {
    const storage = new MemoryStorage();
    let current = await defaultLocalReminderPreference(START);
    for (let index = 1; index <= 105; index += 1) {
      current = await replaceLocalReminderPreference(
        storage,
        current,
        index % 2 ? "in_app_when_available" : "off",
        new Date(Date.parse(START) + index * 60_000).toISOString(),
      );
    }
    expect(current.revision).toBe(106);
    expect(current.changes).toHaveLength(100);
    expect(current.changes[0]?.revision).toBe(7);
    expect(current.changes.at(-1)?.revision).toBe(106);
    expect((await readLocalReminderPreference(storage, START)).status).toBe("ready");
  });

  it("falls back safely without overwriting corrupt or unavailable storage", async () => {
    const corrupt = new MemoryStorage();
    corrupt.values.set(LOCAL_REMINDER_STORAGE_KEY, '{"reminder_mode":"automatic"}');
    const invalid = await readLocalReminderPreference(corrupt, START);
    expect(invalid.status).toBe("invalid");
    expect(invalid.envelope.reminder_mode).toBe("off");
    expect(corrupt.writes).toBe(0);

    const unavailable = await readLocalReminderPreference(
      { getItem: () => { throw new Error("blocked"); } },
      START,
    );
    expect(unavailable.status).toBe("unavailable");
    expect(unavailable.envelope.reminder_mode).toBe("off");
  });

  it("fails a rejected write without claiming the preference changed", async () => {
    const initial = await defaultLocalReminderPreference(START);
    await expect(replaceLocalReminderPreference(
      { setItem: () => { throw new Error("full"); } },
      initial,
      "in_app_when_available",
      "2026-10-17T23:01:00Z",
    )).rejects.toMatchObject({ code: "storage_unavailable" });
    await expect(resetLocalReminderPreference(
      new MemoryStorage(),
      initial,
      "2026-10-17T23:01:00Z",
    )).rejects.toBeInstanceOf(LocalReminderPreferenceError);
    await expect(replaceLocalReminderPreference(
      new MemoryStorage(),
      initial,
      "automatic" as never,
      "2026-10-17T23:01:00Z",
    )).rejects.toMatchObject({ code: "invalid_choice" });
  });

  it("exports a separate local record with explicit limitations", async () => {
    const current = await defaultLocalReminderPreference(START);
    const exported = JSON.parse(await exportLocalReminderPreference(current));
    expect(exported.preference).toEqual(current);
    expect(exported).not.toHaveProperty("learner_id");
    expect(exported.limitations).toEqual(expect.arrayContaining([
      expect.stringContaining("does not schedule or send"),
    ]));
  });

  it("uses stable canonical UTF-8 hashing without normalizing text", async () => {
    expect(await canonicalIntegrity({ z: "café", a: [2, 1] })).toBe(
      "a0ac9412584484503b1a79e92798b4c0a143ee606c0fec8734b9e3748a1f5d57",
    );
    expect(await canonicalIntegrity({ z: "cafe\u0301", a: [2, 1] })).not.toBe(
      "a0ac9412584484503b1a79e92798b4c0a143ee606c0fec8734b9e3748a1f5d57",
    );
  });
});
