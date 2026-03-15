/* eslint-disable react-hooks/refs */
import { useImmerReducer } from "use-immer";
import "./App.css";
import TextareaAutosize from "react-textarea-autosize";
import { useRef } from "react";
import { useMutation } from "@tanstack/react-query";

function App() {
  const initialChatHistory: { role: string; content: string }[] = [
    {
      role: "assistant",
      content: `Hello! I am here to help you learn about Advanced Design System software from the ADS Cookbook.`,
    },
    {
      role: "assistant",
      content: `I am also here to assist you with any pdf documents you upload. Feel free to ask me anything!`,
    },
  ];
  const [chatHistory, dispatchChat] = useImmerReducer(
    chatHistoryReducer,
    initialChatHistory,
  );

  const mutation = useMutation({
    mutationFn: async (
      updatedChatHistory: { role: string; content: string }[],
    ) => {
      const latestUserText =
        updatedChatHistory[updatedChatHistory.length - 1]?.content ?? "";

      const res = await fetch("http://127.0.0.1:4444/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-haiku-4-5", // or "gpt-5-nano"
          embed: "qdrant", // or "snowflake"
          prompt: latestUserText,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Backend error ${res.status}: ${errText}`);
      }

      const data: { response?: string } = await res.json();

      dispatchChat({
        type: "assistant message",
        content: data.response ?? "",
        current_message_index: updatedChatHistory.length - 1,
      });
    },
    onSuccess: () => {
      console.log("AI response successfully processed.");
    },
    onError: (error: Error) => {
      console.error("Error fetching AI response:", error);
      // Optionally, notify the user about the error
    },
  });

  const [TextareaState, dispatchTextareaState] = useImmerReducer(
    textareaStateReducer,
    "",
  );

  const mutationIndex = useRef(0);
  const handleTextareaSubmit = (
    e: React.KeyboardEvent<HTMLTextAreaElement>,
  ) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (TextareaState !== "") {
        dispatchChat({ type: "user message", content: TextareaState });
        dispatchTextareaState({ type: "clear state" });
        // refetch();
        const updatedChatHistory: { role: string; content: string }[] = [
          ...chatHistory,
          { role: "user", content: TextareaState },
        ];
        mutationIndex.current = updatedChatHistory.length - 1;
        mutation.mutate(updatedChatHistory);
      }
    } else if (e.key === "Enter" && e.shiftKey) {
      // Allow Shift + Enter to create a new line
      e.preventDefault();
      const textarea = e.currentTarget;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = textarea.value;
      const newValue = value.substring(0, start) + "\n" + value.substring(end);
      dispatchTextareaState({ type: "set", message: newValue });
      // Move the cursor to the correct position after the newline
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 1;
      }, 0);
    }
  };

  const handleButtonSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (TextareaState !== "") {
      dispatchChat({ type: "user message", content: TextareaState });
      dispatchTextareaState({ type: "clear state" });
      // refetch();
      const updatedChatHistory: { role: string; content: string }[] = [
        ...chatHistory,
        { role: "user", content: TextareaState },
      ];
      mutationIndex.current = updatedChatHistory.length - 1;
      mutation.mutate(updatedChatHistory);
    }
  };

  const mutationFiles = useMutation({
    mutationFn: async (files: File[]) => {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const res = await fetch("http://127.0.0.1:4444/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(`Backend error ${res.status}: ${errText}`);
      }

      return (await res.json()) as { status?: string };
    },
    onSuccess: (data) => {
      if (data?.status === "success") {
        dispatchChat({
          type: "assistant message",
          content:
            "Your PDF(s) have been processed and are ready—ask me questions about them anytime.",
          // set this to "current last index" so your reducer pushes a new assistant message
          current_message_index: chatHistory.length - 1,
        });
      } else {
        console.warn("Upload succeeded but unexpected response:", data);
      }
    },
    onError: (error: Error) => {
      console.error("Error processing PDF(s):", error);
      // Optionally, notify the user about the error
    },
  });

  const handleFilesSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    mutationFiles.mutate(Array.from(e.target.files));
  };

  return (
    <div className="flex flex-col text-base-content h-full bg-base-200 overscroll-none">
      <div className="flex w-full grow flex-col overflow-y-auto overscroll-none px-4 pt-4 pb-0">
        <section className="h-full grow overflow-y-auto overscroll-none">
          {chatHistory.map(
            (message: { role: string; content: string }, i: number) =>
              message.role === "assistant" ? (
                <div
                  key={`${message.role}-${i}`}
                  className={
                    i === chatHistory.length - 1
                      ? "chat chat-start pb-2"
                      : "chat chat-start"
                  }
                >
                  <div className="chat-header">AI Assistant</div>
                  <div className="chat-bubble">
                    {mutation.isPending && i === mutationIndex.current ? (
                      <span className="loading loading-dots loading-sm"></span>
                    ) : (
                      <article>
                        {typeof message.content === "string"
                          ? message.content
                          : ""}
                      </article>
                    )}
                  </div>
                </div>
              ) : message.role === "user" ? (
                <div key={`${message.role}-${i}`} className="chat chat-end">
                  <div className="chat-header">You</div>
                  <div className="chat-bubble">
                    {typeof message.content === "string" ? message.content : ""}
                  </div>
                </div>
              ) : (
                <></>
              ),
          )}
        </section>
      </div>
      <div className="grow-0 p-2 pt-0">
        <form className="size-full" onSubmit={handleButtonSubmit}>
          <div className="join join-horizontal size-full grow-0 p-0">
            <input
              type="file"
              accept=".pdf"
              className="file-input join-item h-full"
              multiple
              onChange={handleFilesSelected}
            />
            <TextareaAutosize
              className="textarea join-item h-auto min-h-0 w-full resize-none"
              placeholder="Ask GPT"
              maxLength={3000}
              minRows={1} // Start at 1 row
              maxRows={3} // Expand up to 3 rows
              value={TextareaState}
              onChange={(e) =>
                dispatchTextareaState({ type: "set", message: e.target.value })
              }
              onKeyDown={(e) => handleTextareaSubmit(e)}
              disabled={mutation.isPending}
              autoFocus
            />
            <button
              type="submit"
              className="btn btn-secondary join-item h-full"
              disabled={mutation.isPending}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="size-6"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5"
                />
              </svg>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function chatHistoryReducer(
  draftState: { role: string; content: string }[],
  action: { type: string; content: string; current_message_index?: number },
): void | { role: string; content: string }[] {
  switch (action.type) {
    case "assistant message": {
      if (action.current_message_index === draftState.length - 1) {
        draftState.push({ role: "assistant", content: action.content });
      } else {
        draftState[draftState.length - 1].content += action.content;
      }
      break;
    }
    case "user message": {
      draftState.push({ role: "user", content: action.content });
      break;
    }
    default: {
      throw new Error(`Unhandled action type: ${action.type}`);
    }
  }
  return draftState;
}

function textareaStateReducer(
  draft: string,
  action: { type: string; message?: string },
) {
  switch (action.type) {
    case "set":
      return action.message;
    case "clear state":
      return "";
    default:
      return draft;
  }
}

export default App;
