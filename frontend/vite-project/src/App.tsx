import "./App.css";
import TextareaAutosize from "react-textarea-autosize";

function App() {
  return (
    <div className="flex flex-col text-base-content h-full bg-base-200 overscroll-none">
      <div className="flex w-80 max-w-full grow flex-col overflow-y-auto overscroll-none px-4 pt-4 pb-0">
        <section className="h-full grow overflow-y-auto overscroll-none"></section>
      </div>
      <div className="grow-0 p-2 pt-0">
        <form className="size-full" onSubmit={(e) => e.preventDefault()}>
          <div className="join join-horizontal size-full grow-0 p-0">
            <input
              type="file"
              className="file-input join-item h-full"
              multiple
            />
            <TextareaAutosize
              className="textarea join-item h-auto min-h-0 w-full resize-none"
              placeholder="Ask GPT"
              maxLength={3000}
              minRows={1} // Start at 1 row
              maxRows={3} // Expand up to 3 rows
              // value={TextareaState}
              // onChange={(e) =>
              //   dispatchTextareaState({ type: "set", message: e.target.value })
              // }
              // onKeyDown={(e) => handleTextareaSubmit(e)}
              // disabled={mutation.isPending}
              autoFocus
            />
            <button
              type="submit"
              className="btn btn-secondary join-item h-full"
              // disabled={mutation.isPending}
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

export default App;
