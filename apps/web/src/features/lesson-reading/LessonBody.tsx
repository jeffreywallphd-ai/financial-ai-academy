import { Fragment, createElement } from "react";
import type { ReactNode } from "react";

import type { components } from "../../generated/api-client";
import type { Lesson } from "./model";


type Schemas = components["schemas"];
type InlineNode =
  | Schemas["AssetImageModel"]
  | Schemas["EmphasisModel"]
  | Schemas["HardBreakModel"]
  | Schemas["InlineCodeModel"]
  | Schemas["InlineTextModel"]
  | Schemas["SoftBreakModel"]
  | Schemas["SourceLinkModel"]
  | Schemas["StrongModel"];
type BodyNode = Lesson["body"][number];

export class InvalidLessonContentError extends Error {
  constructor() {
    super("The lesson contains an unsupported safe-content node.");
  }
}

function InlineNodes({
  assets,
  nodes,
}: {
  assets: Lesson["assets"];
  nodes: ReadonlyArray<InlineNode>;
}) {
  return nodes.map((node, index) => (
    <Fragment key={index}>{renderInlineNode(node, assets)}</Fragment>
  ));
}

function renderInlineNode(
  node: InlineNode,
  assets: Lesson["assets"],
): ReactNode {
  switch (node.kind) {
    case "text":
      return node.value;
    case "code":
      return <code>{node.value}</code>;
    case "soft_break":
      return " ";
    case "hard_break":
      return <br />;
    case "emphasis":
      return (
        <em>
          <InlineNodes assets={assets} nodes={node.children} />
        </em>
      );
    case "strong":
      return (
        <strong>
          <InlineNodes assets={assets} nodes={node.children} />
        </strong>
      );
    case "source_link":
      return (
        <a
          href={node.href}
          rel="noopener noreferrer"
          target="_blank"
        >
          <InlineNodes assets={assets} nodes={node.children} />
          <span className="visually-hidden"> (opens in a new tab)</span>
        </a>
      );
    case "asset_image": {
      const asset = assets.find(
        (candidate) => candidate.asset_id === node.asset_id,
      );
      if (!asset) {
        throw new InvalidLessonContentError();
      }
      return (
        <img
          alt={node.alt_text}
          decoding="async"
          loading="lazy"
          src={asset.locator}
        />
      );
    }
    default:
      throw new InvalidLessonContentError();
  }
}

function BodyNodes({
  assets,
  nodes,
}: {
  assets: Lesson["assets"];
  nodes: ReadonlyArray<BodyNode>;
}) {
  return nodes.map((node, index) => (
    <Fragment key={index}>{renderBodyNode(node, assets)}</Fragment>
  ));
}

function renderBodyNode(
  node: BodyNode,
  assets: Lesson["assets"],
): ReactNode {
  switch (node.kind) {
    case "heading": {
      const tag = ("h" + String(node.level)) as
        | "h1"
        | "h2"
        | "h3"
        | "h4"
        | "h5"
        | "h6";
      return createElement(
        tag,
        null,
        <InlineNodes assets={assets} nodes={node.children} />,
      );
    }
    case "paragraph":
      return (
        <p>
          <InlineNodes assets={assets} nodes={node.children} />
        </p>
      );
    case "code_block":
      return (
        <pre>
          <code data-language={node.language ?? undefined}>
            {node.code}
          </code>
        </pre>
      );
    case "thematic_break":
      return <hr />;
    case "bullet_list":
      return (
        <ul>
          {node.items.map((item, index) => (
            <li key={index}>
              <BodyNodes assets={assets} nodes={item.blocks} />
            </li>
          ))}
        </ul>
      );
    case "ordered_list":
      return (
        <ol start={node.start}>
          {node.items.map((item, index) => (
            <li key={index}>
              <BodyNodes assets={assets} nodes={item.blocks} />
            </li>
          ))}
        </ol>
      );
    default:
      throw new InvalidLessonContentError();
  }
}

export function LessonBody({ lesson }: { lesson: Lesson }) {
  return (
    <div className="lesson-body">
      <BodyNodes assets={lesson.assets} nodes={lesson.body} />
    </div>
  );
}
