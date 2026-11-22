import { cn } from "../../lib/utils.js";

export default function PageContainer({ as: Tag = "div", className, children, ...props }) {
  return <Tag className={cn("mx-auto w-full max-w-page px-5 md:px-8", className)} {...props}>{children}</Tag>;
}
