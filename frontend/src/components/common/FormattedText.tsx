// Render the supported emphasis syntax as React nodes; raw HTML stays escaped.
export default function FormattedText({ text }: { text: string }) {
 return <p className="post-text">{text.split(/(\*\*[^*\n]+\*\*|\*[^*\n]+\*)/g).map((part,i)=>part.startsWith('**') && part.endsWith('**') ? <strong key={i}>{part.slice(2,-2)}</strong> : part.startsWith('*') && part.endsWith('*') ? <em key={i}>{part.slice(1,-1)}</em> : part)}</p>;
}
