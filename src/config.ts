import type {
	ExpressiveCodeConfig,
	LicenseConfig,
	NavBarConfig,
	ProfileConfig,
	SiteConfig,
} from "./types/config";
import { LinkPreset } from "./types/config";

export const siteConfig: SiteConfig = {
	title: "KismetPro",
	subtitle: "我的小破站",
	lang: "zh_CN", // 语言代码，例如 'en'、'zh_CN'、'ja' 等
	themeColor: {
		hue: 220, // 主题颜色的默认色相值，范围从 0 到 360。例如：红色 0，青色 200，蓝色 250，粉色 345
		fixed: false, // 是否隐藏主题色选择器（对访问者）
	},
	banner: {
		enable: true,
		src: "assets/images/demo-banner.png", // 相对于 /src 目录的路径。如果以 '/' 开头，则相对于 /public 目录
		position: "center", // 等同于 object-position，仅支持 'top'、'center'、'bottom'。默认是 'center'
		credit: {
			enable: false, // 是否显示横幅图片的署名文本
			text: "", // 要显示的署名文本
			url: "", // （可选）原图或作者主页的链接
		},
	},
	toc: {
		enable: true, // 是否在文章右侧显示目录（Table of Contents）
		depth: 2, // 目录中显示的标题最大深度，范围从 1 到 3
	},
	favicon: [
		// 如果此数组为空，则使用默认的 favicon
		 {
		   src: '/favicon/icon.png',    // favicon 的路径，相对于 /public 目录
		//   theme: 'light',              // （可选）'light' 或 'dark'，仅在你有明暗模式不同图标时设置
		//   sizes: '32x32',              // （可选）favicon 的尺寸，如果你有不同尺寸的图标
		 }
	],
};

export const navBarConfig: NavBarConfig = {
	links: [
		LinkPreset.Home,
		LinkPreset.Archive,
		LinkPreset.About,
		{
			name: "GitHub",
			url: "https://github.com/kismetpro", // 内部链接不应包含基础路径，会自动添加
			external: true, // 显示外部链接图标，并在新标签页中打开
		},
	],
};

export const profileConfig: ProfileConfig = {
	avatar: "assets/images/demo-avatar.png", // 相对于 /src 目录的路径。如果以 '/' 开头，则相对于 /public 目录
	name: "KismetPro",
	bio: "如无必要，勿增实体",
	links: [
		// {
		// 	name: "Twitter",
		// 	icon: "fa6-brands:twitter", // 图标代码可在 https://icones.js.org/ 查询
		// 	// 如果图标集未包含，需要安装对应的包
		// 	// 例如执行 `pnpm add @iconify-json/<icon-set-name>`
		// 	url: "https://twitter.com",
		// },
		// {
		// 	name: "Steam",
		// 	icon: "fa6-brands:steam",
		// 	url: "https://store.steampowered.com",
		// },
		{
			name: "GitHub",
			icon: "fa6-brands:github",
			url: "https://github.com/saicaca/fuwari",
		},
	],
};

export const licenseConfig: LicenseConfig = {
	enable: true,
	name: "CC BY-NC-SA 4.0",
	url: "https://creativecommons.org/licenses/by-nc-sa/4.0/",
};

export const expressiveCodeConfig: ExpressiveCodeConfig = {
	// 注意：某些样式（如背景色）会被覆盖，详情见 astro.config.mjs 文件
	// 请务必选择深色主题，因为当前博客主题仅支持深色背景
	theme: "github-dark",
};
