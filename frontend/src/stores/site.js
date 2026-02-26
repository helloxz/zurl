import { defineStore } from "pinia";
import req from "@/utils/req";
import { ElMessage } from 'element-plus'

export const useSiteStore = defineStore('site',{
    state:()=>({
        app_info:{},
        email:"",
        username:"",
        is_login:false,
        language: "en", // 当前语言
        site_info:{
            title:"",
            description:"",
            keywords:"",
            author:"",
            footer:"",
            allow_guest_shorten: true,  // 是否允许未登录用户创建短链，默认 true
        },
    }),
    actions:{
        formatDateTime(dateTimeString) {
            if (!dateTimeString) {
              return '';
            }
            
            let date;
            // 检查是否为 Unix 时间戳（10位数字）
            if (typeof dateTimeString === 'number' || (typeof dateTimeString === 'string' && /^\d{10}$/.test(dateTimeString))) {
                // Unix 时间戳需要转换为毫秒
                date = new Date(parseInt(dateTimeString) * 1000);
            } else {
                // 日期字符串直接创建 Date 对象
                date = new Date(dateTimeString);
            }
          
            // 获取年份、月份、日期、小时和分钟
            const year = date.getFullYear();
            const month = String(date.getMonth() + 1).padStart(2, '0'); // 月份从 0 开始，需要加 1，并补零
            const day = String(date.getDate()).padStart(2, '0');
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
          
            // 返回格式化后的字符串
            return `${year}-${month}-${day} ${hours}:${minutes}`;
        },
        async getAppInfo(){
            // 通过session获取app_info
            let app_info = sessionStorage.getItem("app_info");
            // 如果获取到了
            if( app_info ){
                this.app_info = JSON.parse(app_info);
                this.email = this.app_info.email;
                this.username = this.app_info.username;
                // this.wp_domain = this.app_info["wordpress.domain"];
                return;
            }
            // 没获取到
            await req.get("/api/get/appinfo").then((res)=>{
                if( res.data.code == 200 ){
                    this.app_info = res.data.data;
                    this.email = this.app_info.email;
                    this.username = this.app_info.username;
                    // this.wp_domain = this.app_info["wordpress.domain"];
                    // 写入session中存储
                    sessionStorage.setItem("app_info",JSON.stringify(res.data.data));
                }
                else{
                    console.log(res.data.msg);
                }
            })
        },
        async getSiteInfo(){
            await req.get("/api/option/get_site_info").then((res)=>{
                if( res.data.code == 200 ){
                    this.site_info = res.data.data;
                }
                else if(res.data.code == 404 ) {
                    this.site_info.title = "Zurl"
                }
                else{
                    console.log(res.data.msg);
                }
            })
        },
        // 检查用户是否登录
        async checkLogin() {
            await req.get("/api/user/is_login")
            .then(res=>{
                if( res.data.code == 200) {
                    this.is_login = true;
                    return;
                }
            })
            .catch(err=>{
                if (err.response) {
                    if (err.response.status === 401) {
                        this.is_login = false;
                        // 提示错误
                        ElMessage.error("请先登录！")
                    }
                }
            })
        },
        // 切换语言
        switchLanguage(lang) {
            if (lang && (lang === 'zh' || lang === 'en')) {
                this.language = lang;
                // 保存到 localStorage
                localStorage.setItem('user_language', lang);
                // 刷新页面以应用新语言
                window.location.reload();
            }
        }
    }
})