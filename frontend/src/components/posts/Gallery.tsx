import {useRef,useState} from 'react';
import {mediaUrl} from '../../services/api';
import type {Post} from '../../types';
export default function Gallery({post,compact=false}:{post:Post;compact?:boolean}){
 const photos=post.photos?.length ? post.photos.map(p=>p.url) : post.photo_url ? [post.photo_url] : [];
 const [index,setIndex]=useState(0);const dialog=useRef<HTMLDialogElement>(null);if(!photos.length)return null;
 return <><div className={`post-gallery ${compact ? "compact-post-gallery" : ""}`}>{(compact ? photos.slice(0,2) : photos).map((url,i)=><button type="button" key={url} aria-label={`Открыть фото ${i+1} из ${photos.length}`} onClick={()=>{setIndex(i);dialog.current?.showModal();}}><img src={mediaUrl(url)} alt={`${post.title} — фото ${i+1}`} loading="lazy"/>{compact && i===1 && photos.length>2 && <span className="gallery-more">+{photos.length-2}</span>}</button>)}</div><dialog ref={dialog} className="photo-dialog" aria-label="Просмотр фотографий" onClick={e=>{if(e.target===e.currentTarget)dialog.current?.close();}}><button type="button" className="velo-button" onClick={()=>dialog.current?.close()}>Закрыть</button><img src={mediaUrl(photos[index]||photos[0])} alt={`${post.title} — фото ${index+1}`}/><div className="form-actions"><button type="button" disabled={index===0} onClick={()=>setIndex(i=>i-1)}>← Назад</button><span>{index+1} / {photos.length}</span><button type="button" disabled={index===photos.length-1} onClick={()=>setIndex(i=>i+1)}>Далее →</button></div></dialog></>;
}

