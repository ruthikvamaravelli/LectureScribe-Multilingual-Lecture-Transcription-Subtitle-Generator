const fileInput=document.getElementById("audioFile");
const fileName=document.getElementById("fileName");
const transcribeBtn=document.getElementById("transcribeBtn");
const statusBox=document.getElementById("status");
const recordBtn=document.getElementById("recordBtn");
const recordStatus=document.getElementById("recordStatus");
const preview=document.getElementById("preview");
let recordedBlob=null, mediaRecorder=null, chunks=[], currentSegments=[];

fileInput.addEventListener("change",()=>{
  recordedBlob=null;
  const file=fileInput.files[0];
  fileName.textContent=file?file.name:"No file selected";
  transcribeBtn.disabled=!file;
  preview.hidden=true;
});

recordBtn.addEventListener("click",async()=>{
  if(mediaRecorder && mediaRecorder.state==="recording"){
    mediaRecorder.stop(); return;
  }
  try{
    const stream=await navigator.mediaDevices.getUserMedia({audio:true});
    chunks=[];
    mediaRecorder=new MediaRecorder(stream);
    mediaRecorder.ondataavailable=e=>{if(e.data.size)chunks.push(e.data)};
    mediaRecorder.onstop=()=>{
      recordedBlob=new Blob(chunks,{type:mediaRecorder.mimeType||"audio/webm"});
      const ext=(recordedBlob.type.includes("ogg")?"ogg":"webm");
      recordedBlob.name=`lecture-recording.${ext}`;
      preview.src=URL.createObjectURL(recordedBlob);
      preview.hidden=false;
      fileInput.value="";
      fileName.textContent="Recorded audio ready";
      transcribeBtn.disabled=false;
      stream.getTracks().forEach(t=>t.stop());
      recordBtn.textContent="● Record again";
      recordStatus.textContent="Recording saved";
    };
    mediaRecorder.start();
    recordBtn.textContent="■ Stop recording";
    recordStatus.textContent="Recording…";
  }catch(err){recordStatus.textContent="Microphone access was not granted.";}
});

transcribeBtn.addEventListener("click",async()=>{
  const file=recordedBlob || fileInput.files[0];
  if(!file)return;
  const form=new FormData(); form.append("audio",file,file.name||"recording.webm");
  transcribeBtn.disabled=true; statusBox.textContent="Preparing audio and running speech recognition…";
  try{
    const response=await fetch("/transcribe",{method:"POST",body:form});
    const data=await response.json();
    if(!response.ok)throw new Error(data.error||"Transcription failed");
    document.getElementById("transcript").value=data.text;
    document.getElementById("language").textContent=`Detected language: ${data.language}`;
    currentSegments=data.segments||[];
    const container=document.getElementById("segments"); container.innerHTML="";
    currentSegments.forEach(s=>{
      const row=document.createElement("div");row.className="segment";
      const time=document.createElement("span");time.className="time";
      time.textContent=`${formatTime(s.start)} – ${formatTime(s.end)}`;
      const text=document.createElement("span");text.textContent=s.text;
      row.append(time,text);container.append(row);
    });
    document.getElementById("resultPanel").hidden=false;
    statusBox.textContent="Transcription completed successfully.";
  }catch(err){statusBox.textContent=err.message;}
  finally{transcribeBtn.disabled=false;}
});

document.querySelectorAll("[data-export]").forEach(btn=>btn.addEventListener("click",async()=>{
  const format=btn.dataset.export;
  const response=await fetch("/export",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({format,text:document.getElementById("transcript").value,segments:currentSegments})});
  if(!response.ok){statusBox.textContent="Could not export this file.";return;}
  const blob=await response.blob(),url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download=`lecture-transcript.${format}`;a.click();URL.revokeObjectURL(url);
}));

function formatTime(sec){const m=Math.floor(sec/60),s=Math.floor(sec%60);return `${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;}
